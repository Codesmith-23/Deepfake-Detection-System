import os
import json
import cv2
from mtcnn import MTCNN

# Paths
video_dir = "train_sample_videos"
output_dir = "dataset"
metadata_path = "train_sample_videos/metadata.json"

# Create output dirs
os.makedirs(os.path.join(output_dir, "real"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "fake"), exist_ok=True)

# Load metadata
with open(metadata_path, "r") as f:
    metadata = json.load(f)

detector = MTCNN()

def extract_faces(video_path, label, video_name):
    cap = cv2.VideoCapture(video_path)
    frame_no = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_no += 1
        if frame_no % 10 != 0:  # Process every 10th frame
            continue

        # Detect faces
        faces = detector.detect_faces(frame)
        for i, face in enumerate(faces):
            x, y, w, h = face['box']
            x, y = abs(x), abs(y)
            cropped_face = frame[y:y+h, x:x+w]

            if cropped_face.size == 0:
                continue

            # Save face
            filename = f"{video_name}_frame{frame_no}_face{i}.jpg"
            save_path = os.path.join(output_dir, label.lower(), filename)
            cv2.imwrite(save_path, cropped_face)

    cap.release()

# Loop through metadata
for video_name, info in metadata.items():
    label = info["label"]  # REAL / FAKE
    video_path = os.path.join(video_dir, video_name)

    if os.path.exists(video_path):
        print(f"Processing {video_name} ({label})...")
        extract_faces(video_path, label, os.path.splitext(video_name)[0])
    else:
        print(f"Video not found: {video_name}")
