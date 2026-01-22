import matplotlib
matplotlib.use('Agg')  # FIX 1: Prevent Windows Display Deadlock
import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf  # FIX 2: Faster, robust audio loading
from joblib import Parallel, delayed
from tqdm import tqdm
import glob

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Moinuddin's Projects\Voice Deepfake\Dataset\LA"
OUTPUT_BASE_DIR = os.path.join(BASE_PATH, "processed_images")
IMG_SIZE = (128, 128)
DURATION = 4.0

def find_protocol_file(base_path):
    search_pattern = os.path.join(base_path, "**", "ASVspoof2019.LA.cm.train.trn.txt")
    files = glob.glob(search_pattern, recursive=True)
    if files: return files[0]
    
    # Fallback
    search_pattern_old = os.path.join(base_path, "**", "ASVspoof2019.LA.cm.train.trl.txt")
    files_old = glob.glob(search_pattern_old, recursive=True)
    return files_old[0] if files_old else None

def find_audio_dir(base_path):
    search_pattern = os.path.join(base_path, "**", "ASVspoof2019_LA_train", "flac")
    dirs = glob.glob(search_pattern, recursive=True)
    return dirs[0] if dirs else None

def process_one_file(line, source_audio_dir):
    try:
        parts = line.strip().split()
        filename = parts[1]    # e.g., LA_T_1138215
        label = parts[4]       # 'bonafide' or 'spoof'
        
        category = 'real' if label == 'bonafide' else 'fake'
        
        input_path = os.path.join(source_audio_dir, filename + ".flac")
        output_path = os.path.join(OUTPUT_BASE_DIR, 'train', category, filename + ".png")

        # Skip if already done (Resume capability)
        if os.path.exists(output_path): return
        if not os.path.exists(input_path): return

        # --- FIX 2 & 3: Direct Read + Stereo Handling ---
        # Read audio directly using soundfile (bypassing librosa.load freeze)
        y, sr = sf.read(input_path)
        
        # If Stereo (2 channels), average to Mono
        if y.ndim > 1:
            y = np.mean(y, axis=1)

        # Pad or Crop to Duration
        target_len = int(DURATION * sr)
        if len(y) < target_len:
            y = np.pad(y, (0, target_len - len(y)))
        else:
            y = y[:target_len]

        # Generate Mel-Spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        S_dB = librosa.power_to_db(S, ref=np.max)

        # Plot and Save (Headless)
        plt.figure(figsize=(2, 2))
        plt.axis('off')
        librosa.display.specshow(S_dB, sr=sr)
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close() # Close memory immediately

    except Exception as e:
        # Silent fail is okay for bulk processing, but printing helps debugging
        # print(f"Error on {filename}: {e}") 
        pass

def main():
    print(" Auto-detecting file paths...")
    
    protocol_file = find_protocol_file(BASE_PATH)
    if not protocol_file:
        print(" CRITICAL ERROR: Could not find protocol file.")
        return
    print(f" Found Protocol: {protocol_file}")

    source_audio_dir = find_audio_dir(BASE_PATH)
    if not source_audio_dir:
        print("❌ CRITICAL ERROR: Could not find audio folder.")
        return
    print(f" Found Audio: {source_audio_dir}")

    # Create Output Folders
    for category in ['real', 'fake']:
        os.makedirs(os.path.join(OUTPUT_BASE_DIR, 'train', category), exist_ok=True)

    with open(protocol_file, 'r') as f:
        lines = f.readlines()

    print(f" Found {len(lines)} files. Starting Processing...")
    
    # Run Parallel (Safe Mode: n_jobs=4 for Windows)
    Parallel(n_jobs=4)(delayed(process_one_file)(line, source_audio_dir) for line in tqdm(lines))
    
    print("\n DONE! Check your 'processed_images' folder.")

if __name__ == "__main__":
    main()