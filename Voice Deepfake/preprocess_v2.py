import os
import pandas as pd
import librosa
import numpy as np
import torch
from tqdm import tqdm

# --- CONFIG ---
CSV_PATH = "Dataset/composite_dataset.csv"
OUTPUT_DIR = "Dataset/Processed_Tensors"
TARGET_SR = 16000
DURATION = 4.0 # Seconds
# --------------

# 1. Setup Output Folder
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. Load CSV
df = pd.read_csv(CSV_PATH)
print(f" Starting Preprocessing for {len(df)} files...")

valid_data = []

# 3. Process Loop
for idx, row in tqdm(df.iterrows(), total=len(df)):
    file_path = row['path']
    label = row['label']
    source = row['source']
    
    # Create a unique filename for the processed file
    # e.g., "ASV2019_LA_12345.pt"
    filename = os.path.basename(file_path).split('.')[0]
    save_name = f"{source}_{filename}.pt"
    save_path = os.path.join(OUTPUT_DIR, save_name)
    
    try:
        # A. LOAD AUDIO
        y, sr = librosa.load(file_path, sr=TARGET_SR)
        
        # B. PAD/CROP to exact length
        num_samples = int(TARGET_SR * DURATION)
        if len(y) > num_samples:
            start = (len(y) - num_samples) // 2
            y = y[start : start + num_samples]
        else:
            padding = num_samples - len(y)
            y = np.pad(y, (0, padding), mode='constant')
            
        # C. MEL SPECTROGRAM
        mel_spec = librosa.feature.melspectrogram(y=y, sr=TARGET_SR, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # D. NORMALIZE (0 to 1)
        mel_spec_db = (mel_spec_db + 80) / 80
        
        # E. RESIZE TO 128x128 (For CNN Compatibility)
        tensor = torch.tensor(mel_spec_db).float().unsqueeze(0).unsqueeze(0) # Add Batch & Channel dims
        tensor = torch.nn.functional.interpolate(tensor, size=(128, 128), mode='bilinear').squeeze(0)
        
        # F. SAVE TENSOR
        torch.save(tensor, save_path)
        
        # Add to new index
        valid_data.append({
            "path": save_path, # Points to the .pt file now!
            "label": label,
            "source": source
        })

    except Exception as e:
        # print(f"Error processing {file_path}: {e}")
        pass

# 4. Save NEW CSV
new_csv_path = "Dataset/processed_dataset.csv"
pd.DataFrame(valid_data).to_csv(new_csv_path, index=False)
print(f"\n Done! Processed {len(valid_data)} files.")
print(f" New manifest saved to: {new_csv_path}")
print(" Use this new CSV for training!")