import os
import pandas as pd

# ================= CONFIGURATION =================
BASE_DIR = os.getcwd() 

PATHS = {
    # --- ASVspoof 2019 LA ---
    "ASV19_AUDIO": os.path.join(BASE_DIR, "Dataset", "LA", "ASVspoof2019_LA_train", "flac"),
    "ASV19_KEYS":  os.path.join(BASE_DIR, "Dataset", "LA", "ASVspoof2019_LA_cm_protocols", "ASVspoof2019.LA.cm.train.trn.txt"),
    
    # --- ASVspoof 2021 DF ---
    "ASV21_AUDIO": os.path.join(BASE_DIR, "Dataset", "ASVspoof2021_DF_eval", "flac"),
    "ASV21_KEYS":  os.path.join(BASE_DIR, "Dataset", "keys", "DF","CM","trial_metadata.txt"),
    
    # --- In The Wild (The folder with WAVs + meta.csv) ---
    # Update this if your folder name is different after extraction!
    "ITW_FOLDER":   os.path.join(BASE_DIR, "Dataset", "InTheWild", "release_in_the_wild"),
}

# =================================================

data = []
print(f" Starting Data Fusion in {BASE_DIR}...")

# ---------------------------------------------------------
# PART 1: ASVspoof 2019 LA
# ---------------------------------------------------------
print("1 Scanning ASVspoof 2019 LA...")
if os.path.exists(PATHS["ASV19_KEYS"]):
    if os.path.exists(PATHS["ASV19_AUDIO"]):
        count = 0
        with open(PATHS["ASV19_KEYS"], 'r') as f:
            for line in f:
                parts = line.strip().split()
                filename = parts[1]
                label_text = parts[-1] 
                
                full_path = os.path.join(PATHS["ASV19_AUDIO"], filename + ".flac")
                
                if os.path.exists(full_path):
                    data.append({
                        "path": full_path,
                        "label": 1 if label_text == "spoof" else 0,
                        "source": "ASV2019_LA"
                    })
                    count += 1
        print(f"   -> Found {count} samples.")
    else:
        print(f"  ERROR: Audio folder missing: {PATHS['ASV19_AUDIO']}")
else:
    print(f"  ERROR: Keys missing: {PATHS['ASV19_KEYS']}")


# ---------------------------------------------------------
# PART 2: ASVspoof 2021 DF
# ---------------------------------------------------------
print("2  Scanning ASVspoof 2021 DF...")
if os.path.exists(PATHS["ASV21_KEYS"]):
    if os.path.exists(PATHS["ASV21_AUDIO"]):
        existing_21_files = set(os.listdir(PATHS["ASV21_AUDIO"]))
        print(f"   -> Found {len(existing_21_files)} audio files on disk.")
        
        matched_count = 0
        with open(PATHS["ASV21_KEYS"], 'r') as f:
            for line in f:
                parts = line.strip().split()
                filename = parts[0]
                label_text = parts[-1]
                
                full_filename = filename + ".flac"
                
                if full_filename in existing_21_files:
                    data.append({
                        "path": os.path.join(PATHS["ASV21_AUDIO"], full_filename),
                        "label": 1 if label_text == "spoof" else 0,
                        "source": "ASV2021_DF"
                    })
                    matched_count += 1
        print(f"   -> Successfully matched {matched_count} samples.")
    else:
        print(f"  ERROR: Audio folder missing: {PATHS['ASV21_AUDIO']}")
else:
    print(f"  ERROR: Keys missing: {PATHS['ASV21_KEYS']}")


# ---------------------------------------------------------
# PART 3: In-The-Wild (Using meta.csv)
# ---------------------------------------------------------
print("3  Scanning In-The-Wild...")
csv_path = os.path.join(PATHS["ITW_FOLDER"], "meta.csv")

if os.path.exists(csv_path):
    try:
        # Load the CSV
        df_itw = pd.read_csv(csv_path)
        print(f"   -> Loaded meta.csv with {len(df_itw)} rows.")
        
        # Adjust column names if they are weird (sometimes 'file' is 'filename')
        if 'file' not in df_itw.columns and 'filename' in df_itw.columns:
            df_itw.rename(columns={'filename': 'file'}, inplace=True)
            
        count = 0
        for index, row in df_itw.iterrows():
            filename = str(row['file'])
            label_raw = str(row['label']).lower()
            
            # 1. Handle Extensions
            if not filename.endswith('.wav') and not filename.endswith('.mp3'):
                filename += '.wav'
                
            full_path = os.path.join(PATHS["ITW_FOLDER"], filename)
            
            # 2. Handle Labels (spoof vs bona-fide)
            # The dataset uses 'spoof' for fake and 'bona-fide' for real
            is_fake = 1 if 'spoof' in label_raw else 0
            
            # 3. Verify file exists
            if os.path.exists(full_path):
                data.append({
                    "path": full_path,
                    "label": is_fake,
                    "source": "InTheWild"
                })
                count += 1
                
        print(f"   -> Successfully mapped {count} audio files.")
        
    except Exception as e:
        print(f"  ERROR processing meta.csv: {e}")
        # Fallback: Print the first few lines so we can debug
        print("   -> Tip: Check if the CSV columns are named 'file' and 'label'")

else:
    print(f"  ERROR: meta.csv not found at: {csv_path}")


# ---------------------------------------------------------
# FINAL SAVE
# ---------------------------------------------------------
if len(data) > 0:
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True) # Shuffle
    
    output_path = os.path.join(BASE_DIR, "Dataset", "composite_dataset.csv")
    df.to_csv(output_path, index=False)

    print(f"\n SUCCESS! Generated Manifest: {output_path}")
    print(f" Total Samples: {len(df)}")
    print(df["source"].value_counts())
else:
    print("\n FAILED. No data found. Please check paths in CONFIG section.")