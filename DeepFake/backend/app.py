import os
# --- OPTIMIZATION: Force CPU Mode & Reduce TF Logs ---
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" 

import uuid
import sqlite3
import cv2
import numpy as np
import dlib
import time
import shutil
import gc
import atexit
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
from flask_cors import CORS
import requests 
from moviepy.editor import VideoFileClip 
import traceback
from huggingface_hub import hf_hub_download 



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Allow all for local dev

# JWT Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-2026'  # TODO: Use environment variable
app.config['JWT_EXPIRATION_HOURS'] = 24

ALLOWED_AUDIO = {'.mp3', '.wav', '.flac', '.m4a'}
ALLOWED_VIDEO = {'.mp4', '.avi', '.mov', '.mkv'}

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
VIDEOS_DIR = os.path.join(app.config["UPLOAD_FOLDER"], "videos")
FRAMES_DIR = os.path.join(app.config["UPLOAD_FOLDER"], "flagged_frames")

# Create directories
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

# --- CLEANUP LOGIC ---
def robust_delete(file_path):
    """Retries deletion to handle Windows file locking."""
    if not file_path or not os.path.exists(file_path):
        return
    
    # Force garbage collection to release file handles
    gc.collect()
    
    for i in range(5):
        try:
            os.remove(file_path)
            return
        except PermissionError:
            time.sleep(0.1) # Brief pause
        except Exception as e:
            print(f" Error deleting {file_path}: {e}")

def cleanup_folder(folder_path):
    """Wipes all files in a folder. Used for session resets."""
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f" Failed to clean {filename}: {e}")

# Run cleanup on server startup
cleanup_folder(VIDEOS_DIR)
cleanup_folder(FRAMES_DIR)

# Register cleanup on server exit (Zero Retention Guarantee)
atexit.register(lambda: cleanup_folder(FRAMES_DIR))

# # --- MODEL LOADING ---
# print("Loading model...")
# model = load_model("models/model_fine_final.h5")
# print("Model loaded.")

print("Loading video model from Hugging Face...")
try:
    # Your Repo ID and Filename from the screenshot
    REPO_ID = "Codesmith-23/deepfake-detector-v1"
    FILENAME = "model_fine_final.h5"
    
    model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)
    model = load_model(model_path)
    print(f"Video Model loaded successfully from: {model_path}")
except Exception as e:
    print(f"CRITICAL ERROR: Could not download/load video model. {e}")
    model = None


detector = dlib.get_frontal_face_detector()
DB_PATH = "database.db"

# --- DATABASE ---
def init_db():
    with sqlite3.connect(DB_PATH) as frconn:
        c = frconn.cursor()
        
        # Users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Results table
        c.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                analysisID TEXT,
                file_name TEXT,
                result TEXT,
                confidence TEXT,
                timestamp TEXT,
                file_size TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        frconn.commit()
init_db()

def save_result(user_id, analysisID, file_name, result, confidence, file_size):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO results (user_id, analysisID, file_name, result, confidence, timestamp, file_size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, analysisID, file_name, result, confidence, datetime.now().isoformat(), file_size))
        conn.commit()

# --- AUTHENTICATION UTILITIES ---
def generate_token(user_id, username):
    """Generate JWT token for authenticated user."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return payload if valid."""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

# --- AUTHENTICATION ROUTES ---
@app.route("/auth/register", methods=["POST"])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({"error": "Missing required fields: username, email, password"}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Basic validation
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Invalid email format"}), 400
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert into database
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO users (username, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                """, (username, email, password_hash, datetime.now().isoformat()))
                conn.commit()
                user_id = c.lastrowid
                
                # Generate token for immediate login
                token = generate_token(user_id, username)
                
                return jsonify({
                    "message": "Registration successful",
                    "token": token,
                    "user": {
                        "id": user_id,
                        "username": username,
                        "email": email
                    }
                }), 201
                
            except sqlite3.IntegrityError as e:
                if 'username' in str(e):
                    return jsonify({"error": "Username already exists"}), 409
                elif 'email' in str(e):
                    return jsonify({"error": "Email already registered"}), 409
                else:
                    return jsonify({"error": "Registration failed"}), 500
                    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --- MAIN ROUTE ---
@app.route("/predict/media", methods=["POST"]) 
def predict_media():
    # 1. AUTO-WIPE: Clear previous session's frames immediately
    # This mimics the "new request" cleanup logic you wanted.
    cleanup_folder(FRAMES_DIR)
    
    cv2.ocl.setUseOpenCL(False)
    filepath = None
    temp_extracted_audio = None
    
    try:
        if 'file' not in request.files: return jsonify({"error": "No file"}), 400
        file = request.files["file"]
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        user_id = request.form.get("user_id", "guest")
        analysisID = str(uuid.uuid4())
        
        # Save Video
        save_name = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(VIDEOS_DIR, save_name)
        file.save(filepath)
        file_size = os.path.getsize(filepath)

        # --- A. AUDIO FILE ---
        if ext in ALLOWED_AUDIO:
            audio_data = {"label": "Error", "confidence": 0, "segments": []}
            try:
                with open(filepath, "rb") as f:
                    resp = requests.post("http://127.0.0.1:5001/predict_audio", files={"file": f}, timeout=120)
                    if resp.status_code == 200: audio_data = resp.json()
            except Exception: pass
            
            result = "deepfake" if audio_data['label'] == 'fake' else "authentic"
            confidence = audio_data.get('confidence', 0)
            save_result(user_id, analysisID, filename, result, confidence, file_size)
            
            return jsonify({
                "type": "audio", "result": result, "confidence": confidence,
                "audio_analysis": audio_data, "flaggedFrames": []
            })

        # --- B. VIDEO FILE ---
        elif ext in ALLOWED_VIDEO:
            print(f"Processing Video: {filename}")
            cap = cv2.VideoCapture(filepath)
            frameRate = cap.get(cv2.CAP_PROP_FPS)
            fake_probs = []
            flagged_frames = []

            while cap.isOpened():
                frameId = cap.get(1)
                ret, frame = cap.read()
                if not ret: break
                
                # Efficiency: Process every ~2 seconds
                if frameRate > 0 and frameId % (int(frameRate) * 2 + 1) != 0: continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_rects = detector(gray, 0)

                for i, d in enumerate(face_rects):
                    x1, y1, x2, y2 = max(0, d.left()), max(0, d.top()), min(frame.shape[1], d.right()), min(frame.shape[0], d.bottom())
                    if x2-x1 < 10 or y2-y1 < 10: continue
                    
                    try:
                        crop = cv2.resize(frame[y1:y2, x1:x2], (299, 299)) / 255.0
                        pred = model.predict(crop.reshape(1, 299, 299, 3), verbose=0)[0][0]
                        fake_probs.append(pred)

                        if pred <= 0.5: # Fake Detected
                            t_name = f"{uuid.uuid4()}.jpg"
                            # Save frame to disk (needed for display)
                            cv2.imwrite(os.path.join(FRAMES_DIR, t_name), frame)
                            flagged_frames.append(f"/uploads/flagged_frames/{t_name}")
                    except: continue
            
            cap.release() # Release lock
            
            # Audio Extraction
            audio_data = {"label": "Not Detected", "confidence": 0}
            try:
                clip = VideoFileClip(filepath)
                if clip.audio:
                    temp_extracted_audio = os.path.join(VIDEOS_DIR, f"temp_{uuid.uuid4()}.wav")
                    clip.audio.write_audiofile(temp_extracted_audio, logger=None, verbose=False)
                    clip.close()
                    del clip
                    gc.collect()
                    
                    with open(temp_extracted_audio, "rb") as f:
                        resp = requests.post("http://127.0.0.1:5001/predict_audio", files={"file": f}, timeout=120)
                        if resp.status_code == 200: audio_data = resp.json()
                else: 
                    clip.close()
            except: 
                if 'clip' in locals(): clip.close()

            # Fusion Logic
            avg_prob = np.mean(fake_probs) if fake_probs else 1.0
            video_result = "deepfake" if avg_prob <= 0.5 else "authentic"
            video_conf = round((sum(p <= 0.5 for p in fake_probs) / len(fake_probs) * 100), 2) if fake_probs else 0

            final_result = video_result
            final_conf = video_conf
            if audio_data.get('label') == 'fake':
                final_result = "deepfake"
                final_conf = audio_data['confidence'] if video_result == "authentic" else (video_conf + audio_data['confidence'])/2
            
            save_result(user_id, analysisID, filename, final_result, final_conf, file_size)
            
            # Note: We do NOT delete flagged_frames here. They stay until the NEXT request starts.
            
            return jsonify({
                "type": "video", "result": final_result, "confidence": round(final_conf, 2),
                "video_analysis": {"label": video_result, "conf": video_conf},
                "audio_analysis": audio_data, "flaggedFrames": flagged_frames[:3] if final_result == "deepfake" else []
            })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        # --- STRICT CLEANUP ---
        # 1. Video Input: Deleted immediately (Standard Input Logic)
        robust_delete(filepath)
        # 2. Temp Audio: Deleted immediately
        robust_delete(temp_extracted_audio)
        # 3. Frames: Persist only until the next request starts.

@app.route("/uploads/flagged_frames/<path:filename>")
def serve_flagged_frame(filename):
    # Absolute path serving fixes white boxes
    return send_from_directory(FRAMES_DIR, filename)

@app.route("/history", methods=["POST"])
def get_results():
    user_id = request.json.get("user_id", "guest")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM results WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
            cols = [desc[0] for desc in c.description]
            return jsonify([dict(zip(cols, row)) for row in c.fetchall()])
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/history/delete/<int:result_id>", methods=["DELETE"])
def delete_result(result_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM results WHERE id = ?", (result_id,))
            conn.commit()
        return jsonify({"message": "Result deleted successfully"})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, port=5000)