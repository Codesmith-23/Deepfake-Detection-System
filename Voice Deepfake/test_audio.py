import torch
import torch.nn as nn
import librosa
import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import os

# --- CONFIGURATION ---
MODEL_PATH = "deepfake_model_resnet_lstm.pth"
TEST_FILE_PATH = r"C:\Users\Moinuddin's Projects\Voice Deepfake\test_videos\t2.mp4"  # <--- CAN NOW BE MP4 OR FLAC
IMG_SIZE = (128, 128)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- 1. MODEL ARCHITECTURE ---
class DeepFakeCNN(nn.Module):
    def __init__(self):
        super(DeepFakeCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 16 * 16, 512)
        self.fc2 = nn.Linear(512, 2)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        x = x.view(-1, 128 * 16 * 16)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

def extract_audio_from_video(video_path):
    """Extracts audio from MP4 and saves as temporary WAV"""
    try:
        audio_path = "temp_extracted_audio.wav"
        # Uses ffmpeg (must be installed) or purely librosa if possible
        # Simplest way in python without external ffmpeg tool is librosa directly:
        print("🎬 Video detected! Extracting audio...")
        y, sr = librosa.load(video_path, sr=None) # Librosa can often read MP4 audio directly
        sf.write(audio_path, y, sr)
        return audio_path
    except Exception as e:
        print(f" Could not extract audio. Make sure ffmpeg is installed if librosa fails.\nError: {e}")
        return None

def preprocess_audio(file_path):
    try:
        # Check if it's a video file
        if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            file_path = extract_audio_from_video(file_path)
            if file_path is None: return None

        # Load Audio
        y, sr = sf.read(file_path)
        
        # Stereo to Mono
        if y.ndim > 1:
            y = np.mean(y, axis=1)

        # Fix Length (4 seconds)
        target_len = int(4.0 * sr)
        if len(y) < target_len:
            y = np.pad(y, (0, target_len - len(y)))
        else:
            y = y[:target_len]

        # Mel Spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        S_dB = librosa.power_to_db(S, ref=np.max)

        # Save Temp Image
        plt.figure(figsize=(2, 2))
        plt.axis('off')
        librosa.display.specshow(S_dB, sr=sr)
        plt.savefig("temp_spec.png", bbox_inches='tight', pad_inches=0)
        plt.close()

        # Load as Tensor
        from torchvision import transforms
        from PIL import Image
        transform = transforms.Compose([
            transforms.Resize(IMG_SIZE),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        img = Image.open("temp_spec.png").convert('RGB')
        return transform(img).unsqueeze(0)

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print(f" Loading model...")
    model = DeepFakeCNN().to(device)
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()
    
    print(f" Analyzing: {TEST_FILE_PATH}")
    input_tensor = preprocess_audio(TEST_FILE_PATH)
    
    if input_tensor is None: return

    input_tensor = input_tensor.to(device)
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)
        fake_prob = probs[0][0].item() * 100
        real_prob = probs[0][1].item() * 100

    print("\n" + "="*30)
    print(f" RESULT: {TEST_FILE_PATH}")
    print(f"🔴 FAKE: {fake_prob:.2f}%")
    print(f"🟢 REAL: {real_prob:.2f}%")
    print("="*30)

    # Cleanup temp files
    if os.path.exists("temp_extracted_audio.wav"): os.remove("temp_extracted_audio.wav")
    if os.path.exists("temp_spec.png"): os.remove("temp_spec.png")

if __name__ == "__main__":
    main()