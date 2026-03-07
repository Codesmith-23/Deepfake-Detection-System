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

def token_required(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({"error": "Invalid token format. Use: Bearer <token>"}), 401
        
        if not token:
            return jsonify({"error": "Authentication token missing"}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Pass user info to the route
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

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

@app.route("/auth/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({"error": "Missing username or password"}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            
            if not user:
                return jsonify({"error": "Invalid username or password"}), 401
            
            user_id, username, email, password_hash = user
            
            # Verify password
            if not check_password_hash(password_hash, password):
                return jsonify({"error": "Invalid username or password"}), 401
            
            # Generate token
            token = generate_token(user_id, username)
            
            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": email
                }
            }), 200
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/auth/verify", methods=["GET"])
@token_required
def verify():
    """Verify if the current token is valid."""
    return jsonify({
        "valid": True,
        "user": {
            "id": request.current_user['user_id'],
            "username": request.current_user['username']
        }
    }), 200

# --- MAIN ROUTE ---
@app.route("/predict/media", methods=["POST"]) 
@token_required
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
        user_id = request.current_user['user_id']  # Get from JWT token
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
            
            # Note: Audio files don't have face detection, so no copyright check
            return jsonify({
                "type": "audio", "result": result, "confidence": confidence,
                "audio_analysis": audio_data, "flaggedFrames": [],
                "copyright_check": {"violation_detected": False, "reason": "audio_only_no_face_matching"}
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
            
            # ==========================================
            # PHASE 3: COPYRIGHT VIOLATION DETECTION
            # ==========================================
            # Initialize with default "no violation" status
            copyright_violation = {
                "violation_detected": False,
                "reason": "authentic_content" if final_result == "authentic" else "no_flagged_frames"
            }
            
            if final_result == "deepfake" and len(flagged_frames) > 0:
                print(f"[Phase 3] Synthetic content detected. Checking for copyright violations...")
                
                try:
                    # Extract face from first flagged frame for identity matching
                    flagged_frame_path = flagged_frames[0].lstrip('/')
                    full_flagged_frame_path = os.path.join(BASE_DIR, "uploads", flagged_frame_path)
                    
                    if os.path.exists(full_flagged_frame_path):
                        # Read the flagged frame
                        frame_image = cv2.imread(full_flagged_frame_path)
                        
                        if frame_image is not None:
                            # Encode to base64 for identity service
                            _, frame_encoded = cv2.imencode('.jpg', frame_image)
                            import base64
                            frame_b64 = base64.b64encode(frame_encoded).decode('utf-8')
                            
                            # Call identity service to match identity
                            print(f"[Phase 3] Calling identity service to match against protected identities...")
                            identity_response = requests.post(
                                "http://127.0.0.1:5002/match_identity",
                                json={"image": frame_b64, "threshold": 0.60},
                                timeout=30
                            )
                            
                            if identity_response.status_code == 200:
                                identity_data = identity_response.json()
                                
                                if identity_data.get("match_found"):
                                    matched_entity = identity_data.get("matched_entity", {})
                                    license_status = identity_data.get("license_status", "unknown")
                                    
                                    print(f"[Phase 3] MATCH FOUND: {matched_entity.get('name')} ({matched_entity.get('entity_id')})")
                                    print(f"[Phase 3] License Status: {license_status}")
                                    
                                    # Log violation
                                    try:
                                        with sqlite3.connect("database.db") as conn:
                                            c = conn.cursor()
                                            c.execute("""
                                                INSERT INTO violation_logs (analysis_id, entity_id, matched_confidence, violation_type, flagged_frame_path, timestamp)
                                                VALUES (?, ?, ?, ?, ?, ?)
                                            """, (
                                                analysisID,
                                                matched_entity.get('entity_id'),
                                                matched_entity.get('confidence', 0),
                                                "unauthorized_likeness" if license_status == "unauthorized" else "unknown_rights",
                                                flagged_frames[0],
                                                datetime.now().isoformat()
                                            ))
                                            conn.commit()
                                    except Exception as e:
                                        print(f"[ERROR] Failed to log violation: {e}")
                                    
                                    # Build copyright violation response
                                    copyright_violation = {
                                        "violation_detected": True,
                                        "matched_entity": matched_entity,
                                        "license_status": license_status,
                                        "violation_type": "unauthorized_likeness" if license_status == "unauthorized" else "unknown_rights"
                                    }
                                else:
                                    # No match found
                                    print(f"[Phase 3] No protected identity matched (score: {identity_data.get('closest_match_score', 0):.2f})")
                                    copyright_violation = {
                                        "violation_detected": False,
                                        "reason": "synthetic_but_unregistered"
                                    }
                            else:
                                print(f"[Phase 3] Identity service error: {identity_response.status_code}")
                        else:
                            print(f"[Phase 3] Could not read flagged frame")
                    else:
                        print(f"[Phase 3] Flagged frame not found: {full_flagged_frame_path}")
                
                except Exception as e:
                    print(f"[Phase 3] Error during copyright check: {e}")
                    traceback.print_exc()
            
            # Note: We do NOT delete flagged_frames here. They stay until the NEXT request starts.
            
            # Build response with copyright information
            response_data = {
                "type": "video", 
                "result": final_result, 
                "confidence": round(final_conf, 2),
                "video_analysis": {"label": video_result, "conf": video_conf},
                "audio_analysis": audio_data, 
                "flaggedFrames": flagged_frames[:3] if final_result == "deepfake" else [],
                "copyright_check": copyright_violation
            }
            
            return jsonify(response_data)

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
@token_required
def get_results():
    user_id = request.current_user['user_id']  # Get from JWT token
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM results WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
            cols = [desc[0] for desc in c.description]
            return jsonify([dict(zip(cols, row)) for row in c.fetchall()])
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/history/delete/<int:result_id>", methods=["DELETE"])
@token_required
def delete_result(result_id):
    user_id = request.current_user['user_id']  # Get from JWT token
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            # First check if the result belongs to the user
            c.execute("SELECT user_id FROM results WHERE id = ?", (result_id,))
            result = c.fetchone()
            
            if not result:
                return jsonify({"error": "Result not found"}), 404
            
            if result[0] != user_id:
                return jsonify({"error": "Unauthorized to delete this result"}), 403
            
            # Delete if authorized
            c.execute("DELETE FROM results WHERE id = ?", (result_id,))
            conn.commit()
        return jsonify({"message": "Result deleted successfully"})
    except Exception as e: return jsonify({"error": str(e)}), 500

# ==========================================
# CREATOR REGISTRATION ROUTES (Phase 2)
# ==========================================

@app.route("/creators/register", methods=["POST"])
def register_creator():
    """
    Register a new creator/identity for copyright protection.
    
    Request:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "type": "creator" | "celebrity" | "brand_character",
        "consent": true
    }
    
    Response:
    {
        "entity_id": "creator_abc123",
        "message": "Registration successful",
        "next_step": "upload-references"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ["name", "email", "type", "consent"]
        if not data or not all(k in data for k in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400
        
        name = data["name"].strip()
        email = data["email"].strip().lower()
        creator_type = data["type"]
        consent = data.get("consent", False)
        
        # Validate
        if not name or len(name) < 2:
            return jsonify({"error": "Name must be at least 2 characters"}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Invalid email format"}), 400
        
        if creator_type not in ["creator", "celebrity", "brand_character"]:
            return jsonify({"error": "Invalid type. Must be: creator, celebrity, brand_character"}), 400
        
        if not consent:
            return jsonify({"error": "Consent to biometric data storage is required"}), 400
        
        # Generate entity_id
        entity_id = f"creator_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Call identity service to register
        try:
            # For now, just create the entity. Images will be uploaded separately.
            # The identity service will create the entry when first image is uploaded.
            print(f"[CREATOR] Registering: {name} ({entity_id})")
            
            return jsonify({
                "success": True,
                "entity_id": entity_id,
                "message": "Registration successful. Please upload reference images.",
                "next_step": "upload-references"
            }), 201
        
        except Exception as e:
            print(f"[ERROR] Identity service error: {e}")
            return jsonify({"error": "Failed to register with identity service"}), 500
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/creators/upload-reference", methods=["POST"])
def upload_reference():
    """
    Upload reference images/videos for a creator.
    These will be processed to extract face embeddings.
    
    Request:
    multipart/form-data
    {
        "entity_id": "creator_abc123",
        "files": [image1.jpg, image2.jpg, ...]
    }
    
    Response:
    {
        "success": true,
        "entity_id": "creator_abc123",
        "embeddings_stored": 3,
        "status": "active"
    }
    """
    try:
        entity_id = request.form.get("entity_id")
        
        if not entity_id:
            return jsonify({"error": "Missing entity_id"}), 400
        
        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist("files")
        if not files or len(files) == 0:
            return jsonify({"error": "At least one file is required"}), 400
        
        embeddings_stored = 0
        errors = []
        
        for file in files:
            if file.filename == "":
                continue
            
            try:
                # Read file data
                file_data = file.read()
                
                # Encode to base64 for identity service
                import base64
                image_b64 = base64.b64encode(file_data).decode('utf-8')
                
                # Call identity service to register identity
                identity_response = requests.post(
                    "http://127.0.0.1:5002/register_identity",
                    json={
                        "entity_id": entity_id,
                        "name": entity_id.replace("creator_", "").replace("_", " ").title(),
                        "type": "creator",
                        "image": image_b64
                    },
                    timeout=30
                )
                
                if identity_response.status_code in [201, 200]:
                    embeddings_stored += 1
                    print(f"[UPLOAD] Embedding stored for {entity_id}: {file.filename}")
                else:
                    error_msg = identity_response.json().get("error", "Unknown error")
                    errors.append(f"{file.filename}: {error_msg}")
                    print(f"[ERROR] Failed to register {file.filename}: {error_msg}")
            
            except Exception as e:
                error_msg = f"Failed to process {file.filename}: {str(e)}"
                errors.append(error_msg)
                print(f"[ERROR] {error_msg}")
        
        if embeddings_stored == 0:
            return jsonify({
                "success": False,
                "error": "No embeddings could be stored",
                "details": errors
            }), 400
        
        return jsonify({
            "success": True,
            "entity_id": entity_id,
            "embeddings_stored": embeddings_stored,
            "status": "active",
            "errors": errors if errors else None
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/creators/profile/<entity_id>", methods=["GET"])
def get_creator_profile(entity_id):
    """
    Get creator profile and registration status.
    
    Response:
    {
        "entity_id": "creator_abc123",
        "protection_status": "active",
        "registered_references": 3,
        "matches_found": 0
    }
    """
    try:
        # Call identity service to get profile
        response = requests.get(
            "http://127.0.0.1:5002/list_identities",
            timeout=10
        )
        
        if response.status_code == 200:
            identities = response.json().get("identities", [])
            
            # Find this creator
            creator = next((c for c in identities if c["entity_id"] == entity_id), None)
            
            if not creator:
                return jsonify({
                    "error": "Creator not found"
                }), 404
            
            return jsonify({
                "entity_id": creator["entity_id"],
                "name": creator["name"],
                "type": creator["type"],
                "status": "active" if creator["is_active"] else "inactive",
                "registered_references": creator.get("embedding_count", 0),
                "created_at": creator["created_at"],
                "protection_status": "active" if creator["is_active"] and creator.get("embedding_count", 0) > 0 else "pending"
            }), 200
        else:
            return jsonify({"error": "Failed to fetch creator profile"}), 500
    
    except Exception as e:
        print(f"[ERROR] Failed to get profile for {entity_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/creators/<entity_id>", methods=["DELETE"])
def delete_creator(entity_id):
    """
    Delete a creator and all their data (right to be forgotten).
    
    Response:
    {
        "success": true,
        "message": "Creator deleted successfully"
    }
    """
    try:
        # Call identity service to delete
        response = requests.delete(
            f"http://127.0.0.1:5002/delete_identity/{entity_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                "success": True,
                "message": f"Creator {entity_id} deleted successfully"
            }), 200
        else:
            return jsonify({"error": "Failed to delete creator"}), 500
    
    except Exception as e:
        print(f"[ERROR] Failed to delete {entity_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/creators/list", methods=["GET"])
def list_creators():
    """
    List all registered creators (admin view).
    
    Response:
    {
        "total": 5,
        "creators": [
            {
                "entity_id": "creator_001",
                "name": "John Doe",
                "type": "creator",
                "status": "active",
                "references": 3
            }
        ]
    }
    """
    try:
        response = requests.get(
            "http://127.0.0.1:5002/list_identities",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "total": data.get("total", 0),
                "creators": [
                    {
                        "entity_id": c["entity_id"],
                        "name": c["name"],
                        "type": c["type"],
                        "status": "active" if c["is_active"] else "inactive",
                        "references": c.get("embedding_count", 0),
                        "created_at": c["created_at"]
                    }
                    for c in data.get("identities", [])
                ]
            }), 200
        else:
            return jsonify({"error": "Failed to list creators"}), 500
    
    except Exception as e:
        print(f"[ERROR] Failed to list creators: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, port=5000)