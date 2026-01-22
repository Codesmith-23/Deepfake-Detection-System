import torch
import torch.nn as nn
import torchvision.models as models
import librosa
import numpy as np
import os
import sys
from moviepy.editor import VideoFileClip
from scipy.stats import entropy
from scipy.signal import find_peaks

# ================= CONFIGURATION =================
MODEL_PATH = "deepfake_model_resnet_lstm.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CHUNK_DURATION = 4.0
OVERLAP = 2.0
# =================================================

class ResNetLSTM(nn.Module):
    def __init__(self):
        super(ResNetLSTM, self).__init__()
        resnet = models.resnet34(weights=None)
        resnet.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.feature_extractor = nn.Sequential(*list(resnet.children())[:-2])
        self.lstm = nn.LSTM(input_size=512, hidden_size=256, num_layers=2, batch_first=True, dropout=0.3)
        self.fc = nn.Linear(256, 2)

    def forward(self, x):
        x = self.feature_extractor(x) 
        x = x.mean(dim=2) 
        x = x.permute(0, 2, 1) 
        self.lstm.flatten_parameters()
        x, _ = self.lstm(x)
        x = x[:, -1, :] 
        x = self.fc(x)
        return x

def load_and_convert_audio(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    temp_wav = "temp_audio_extract.wav"
    try:
        if ext in ['.mp4', '.mkv', '.avi', '.mov']:
            try:
                video = VideoFileClip(file_path)
                if video.audio is None:
                    return None
                video.audio.write_audiofile(temp_wav, logger=None, verbose=False)
                return temp_wav
            except:
                return None
        else:
            return file_path
    except Exception as e:
        print(f" Error reading file: {e}")
        return None

# ============= ADVANCED PREPROCESSING WITH METADATA =============
def preprocess_sliding_window_advanced(file_path):
    """
    Enhanced preprocessing that extracts audio chunks AND their quality metadata
    """
    clean_path = load_and_convert_audio(file_path)
    if clean_path is None: 
        return None, None
    
    try:
        y, sr = librosa.load(clean_path, sr=16000)
        
        chunk_samples = int(16000 * CHUNK_DURATION)
        stride_samples = int(16000 * (CHUNK_DURATION - OVERLAP))
        
        if len(y) < chunk_samples:
            y = np.pad(y, (0, chunk_samples - len(y)), mode='constant')
            chunks = [y]
            chunk_starts = [0]
        else:
            chunks = []
            chunk_starts = []
            for start in range(0, len(y) - chunk_samples + 1, stride_samples):
                end = start + chunk_samples
                chunks.append(y[start:end])
                chunk_starts.append(start)
        
        # Process chunks and compute metadata
        tensors = []
        metadata = []
        
        for idx, chunk in enumerate(chunks):
            # Compute chunk quality metrics
            rms_energy = librosa.feature.rms(y=chunk)[0]
            mean_energy = np.mean(rms_energy)
            std_energy = np.std(rms_energy)
            
            # Zero-crossing rate (helps identify noise vs speech)
            zcr = librosa.feature.zero_crossing_rate(chunk)[0]
            mean_zcr = np.mean(zcr)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=chunk, sr=sr)[0]
            mean_centroid = np.mean(spectral_centroids)
            
            # Create spectrogram
            mel_spec = librosa.feature.melspectrogram(y=chunk, sr=16000, n_mels=128)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            mel_spec_db = (mel_spec_db + 80) / 80
            
            # Compute spectrogram entropy (measures randomness/complexity)
            spec_flat = mel_spec.flatten()
            spec_flat = spec_flat[spec_flat > 0]  # Remove zeros
            spec_entropy = entropy(spec_flat / np.sum(spec_flat)) if len(spec_flat) > 0 else 0
            
            tensor = torch.tensor(mel_spec_db).float().unsqueeze(0)
            tensor = torch.nn.functional.interpolate(
                tensor.unsqueeze(0), size=(128, 128), mode='bilinear'
            ).squeeze(0)
            tensors.append(tensor)
            
            # Store metadata for this chunk
            metadata.append({
                'index': idx,
                'start_time': chunk_starts[idx] / sr,
                'energy': mean_energy,
                'energy_std': std_energy,
                'zcr': mean_zcr,
                'spectral_centroid': mean_centroid,
                'spec_entropy': spec_entropy,
                'is_silence': mean_energy < 0.015,  # Lowered threshold for better detection
                'is_noisy': mean_zcr > 0.20  # Raised threshold - less aggressive filtering
            })
        
        if clean_path == "temp_audio_extract.wav" and os.path.exists(clean_path):
            os.remove(clean_path)
        
        if len(tensors) > 0:
            return torch.stack(tensors).to(DEVICE), metadata
        else:
            return None, None
            
    except Exception as e:
        print(f" Error processing: {e}")
        return None, None

# ============= INTELLIGENT PREDICTION AGGREGATION =============
def compute_prediction_confidence(probabilities, metadata):
    """
    Analyzes prediction patterns to compute weighted confidence scores
    """
    fake_probs = probabilities[:, 1].cpu().numpy()
    
    # Filter out silent/noisy chunks (they cause false positives)
    active_indices = [
        i for i, meta in enumerate(metadata) 
        if not meta['is_silence'] and not meta['is_noisy']
    ]
    
    # If too few active chunks, relax the filter to avoid losing all data
    if len(active_indices) < 3:
        # Use less strict filtering - only remove completely silent chunks
        active_indices = [
            i for i, meta in enumerate(metadata) 
            if not meta['is_silence']
        ]
    
    # If still too few, use all chunks
    if len(active_indices) < 2:
        active_indices = list(range(len(fake_probs)))
    
    active_probs = fake_probs[active_indices]
    
    return {
        'filtered_probs': fake_probs,
        'active_probs': active_probs,
        'num_filtered': len(fake_probs),
        'num_active': len(active_indices),
        'active_indices': active_indices
    }

def detect_anomaly_patterns(probs, window_size=3):
    """
    Detects suspicious patterns in probability sequence:
    - Sudden spikes (deepfake artifacts)
    - Sustained high probabilities (consistent deepfake quality)
    """
    if len(probs) < window_size:
        return {
            'has_spikes': False,
            'has_plateau': False,
            'spike_score': 0,
            'plateau_score': 0,
            'num_spikes': 0,
            'plateau_length': 0
        }
    
    # Detect sharp spikes using peak detection
    peaks, properties = find_peaks(probs, prominence=0.15, width=1)
    has_spikes = len(peaks) > 0
    spike_score = np.max(probs[peaks]) if has_spikes else 0
    
    # Detect plateaus (3+ consecutive high values)
    high_threshold = 0.55
    high_regions = probs > high_threshold
    
    max_consecutive = 0
    current_consecutive = 0
    for val in high_regions:
        if val:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0
    
    has_plateau = max_consecutive >= window_size
    plateau_score = np.mean(probs[probs > high_threshold]) if has_plateau else 0
    
    return {
        'has_spikes': has_spikes,
        'has_plateau': has_plateau,
        'spike_score': spike_score,
        'plateau_score': plateau_score,
        'num_spikes': len(peaks),
        'plateau_length': max_consecutive
    }

def compute_statistical_measures(probs):
    """
    Compute robust statistical measures of the probability distribution
    """
    if len(probs) == 0:
        return {'mean': 0, 'median': 0, 'std': 0, 'top3_mean': 0, 'top5_mean': 0}
    
    sorted_probs = np.sort(probs)
    
    return {
        'mean': np.mean(probs),
        'median': np.median(probs),
        'std': np.std(probs),
        'q75': np.percentile(probs, 75),
        'q90': np.percentile(probs, 90),
        'max': np.max(probs),
        'top3_mean': np.mean(sorted_probs[-3:]) if len(probs) >= 3 else np.max(probs),
        'top5_mean': np.mean(sorted_probs[-5:]) if len(probs) >= 5 else np.mean(sorted_probs[-3:])
    }

# ============= MAIN PREDICTION FUNCTION =============
def predict(file_path):
    print(f"\n Loading Model on {DEVICE}...")
    model = ResNetLSTM().to(DEVICE)
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    except FileNotFoundError:
        print(f"❌ Error: Model file '{MODEL_PATH}' not found!")
        return

    model.eval()
    
    batch_tensors, metadata = preprocess_sliding_window_advanced(file_path)
    
    if batch_tensors is None: 
        print(" Could not process audio.")
        return

    print(f" Analyzing {len(batch_tensors)} segments...")

    with torch.no_grad():
        outputs = model(batch_tensors)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        
        # Get confidence metrics
        confidence = compute_prediction_confidence(probabilities, metadata)
        
        # Analyze both all chunks and active (non-silent) chunks
        all_probs = confidence['filtered_probs']
        active_probs = confidence['active_probs']
        
        # Compute statistics on active chunks (more reliable)
        stats = compute_statistical_measures(active_probs)
        patterns = detect_anomaly_patterns(active_probs)
        
        # Display analysis
        print("\n" + "="*50)
        print(f" File: {os.path.basename(file_path)}")
        print("="*50)
        print(f" Chunks: {confidence['num_filtered']} total, {confidence['num_active']} active")
        print(f" Statistics (Active Chunks):")
        print(f"   Mean Confidence: {stats['mean']*100:.1f}%")
        print(f"   Median Confidence: {stats['median']*100:.1f}%")
        print(f"   Max Confidence: {stats['max']*100:.1f}%")
        print(f"   75th Percentile: {stats['q75']*100:.1f}%")
        print(f"   Top-3 Average: {stats['top3_mean']*100:.1f}%")
        
        if patterns['has_spikes']:
            print(f"🔺 Spike Detection: {patterns['num_spikes']} spikes found (max: {patterns['spike_score']*100:.1f}%)")
        if patterns['has_plateau']:
            print(f" Plateau Detection: {patterns['plateau_length']} consecutive suspicious chunks ({patterns['plateau_score']*100:.1f}%)")
        
        # ============= DECISION LOGIC =============
        is_fake = False
        reason = ""
        confidence_score = 0
        
        # RULE 1: Strong Spike Detection (handles obvious deepfakes)
        if patterns['has_spikes'] and patterns['spike_score'] > 0.85:
            is_fake = True
            reason = "Strong Artifact Spike Detected"
            confidence_score = patterns['spike_score'] * 100
        
        # RULE 2: Plateau Detection (handles consistent deepfakes)
        elif patterns['has_plateau'] and patterns['plateau_score'] > 0.65:
            is_fake = True
            reason = "Sustained Anomaly Pattern"
            confidence_score = patterns['plateau_score'] * 100
        
        # RULE 3: High Percentile Test (catches subtle but widespread artifacts)
        elif stats['q75'] > 0.60 and stats['top3_mean'] > 0.65:
            is_fake = True
            reason = "Widespread Anomalies (75th %ile + Top-3)"
            confidence_score = stats['top3_mean'] * 100
        
        # RULE 4: Multiple moderate spikes (intermittent artifacts)
        elif patterns['num_spikes'] >= 2 and stats['top3_mean'] > 0.58:
            is_fake = True
            reason = "Multiple Suspicious Segments"
            confidence_score = stats['top3_mean'] * 100
        
        # RULE 5: Conservative median test (handles edge cases)
        elif stats['median'] > 0.55 and stats['mean'] > 0.50:
            is_fake = True
            reason = "Elevated Median Suspicion"
            confidence_score = stats['median'] * 100
        
        # Default: Real
        else:
            is_fake = False
            reason = "No Significant Anomalies"
            confidence_score = (1 - stats['top3_mean']) * 100
        
        # Output final verdict
        print("\n" + "="*50)
        if is_fake:
            print(f" VERDICT: DEEPFAKE DETECTED")
            print(f"   Reason: {reason}")
            print(f"   Confidence: {confidence_score:.1f}%")
        else:
            print(f" VERDICT: AUTHENTIC HUMAN VOICE")
            print(f"   Reason: {reason}")
            print(f"   Confidence: {confidence_score:.1f}%")
        print("="*50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        raw_input = input("Drag and drop audio/video file here: ")
        path = raw_input.strip()
        if path.startswith("& "): 
            path = path[2:].strip()
        if (path.startswith("'") and path.endswith("'")) or (path.startswith('"') and path.endswith('"')):
            path = path[1:-1]
        path = path.replace("''", "'")

    if os.path.exists(path):
        predict(path)
    else:
        print(f"\n❌ Error: File not found at path: {path}")