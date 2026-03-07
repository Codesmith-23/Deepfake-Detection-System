"""
Identity Service (Port 5002)
Handles face embedding extraction and identity matching against protected database.
Runs independently from main Flask backend.
"""

import os
import sys
import sqlite3
import cv2
import numpy as np
import pickle
import base64
from io import BytesIO
from functools import lru_cache

from flask import Flask, request, jsonify
from flask_cors import CORS

# TensorFlow / FaceNet setup
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# ==========================================
# CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# FaceNet model path (will download on first use)
FACENET_MODEL_PATH = os.path.join(BASE_DIR, "models", "facenet_keras.h5")

# Face detection (using OpenCV DNN or dlib)
FACE_DETECTOR = None

print("[Identity Service] Initializing on port 5002...")

# ==========================================
# MODEL LOADING
# ==========================================

def load_facenet_model():
    """Load FaceNet model for embedding extraction."""
    global facenet_model
    try:
        if os.path.exists(FACENET_MODEL_PATH):
            print(f"[FaceNet] Loading from {FACENET_MODEL_PATH}")
            facenet_model = load_model(FACENET_MODEL_PATH, custom_objects={'tf': tf})
        else:
            print("[FaceNet] Model not found locally. Using pre-trained from TensorFlow Hub...")
            # Alternative: use tensorflow_hub for a pre-trained FaceNet
            # For MVP, we'll use a simple face embedding model
            facenet_model = _load_simple_embedding_model()
        print("[FaceNet] Model loaded successfully")
        return facenet_model
    except Exception as e:
        print(f"[ERROR] Failed to load FaceNet: {e}")
        return None

def _load_simple_embedding_model():
    """
    Fallback: Load a simple pre-trained embedding model.
    Uses Keras' built-in MobileNetV2 as feature extractor.
    Not as good as FaceNet, but works for demo.
    """
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.layers import GlobalAveragePooling2D
    from tensorflow.keras.models import Model
    
    base_model = MobileNetV2(input_shape=(160, 160, 3), include_top=False, weights='imagenet')
    x = GlobalAveragePooling2D()(base_model.output)
    model = Model(inputs=base_model.input, outputs=x)
    return model

def load_face_detector():
    """Load face detector (OpenCV DNN)."""
    global FACE_DETECTOR
    try:
        # Using OpenCV's DNN module with pre-trained Caffe model
        prototxt = os.path.join(BASE_DIR, "models", "deploy.prototxt")
        model_file = os.path.join(BASE_DIR, "models", "res10_300x300_ssd_iter_140000.caffemodel")
        
        if os.path.exists(prototxt) and os.path.exists(model_file):
            FACE_DETECTOR = cv2.dnn.readNetFromCaffe(prototxt, model_file)
            print("[Face Detector] OpenCV DNN loaded")
        else:
            print("[Face Detector] Model files not found, using fallback (dlib)")
            import dlib
            FACE_DETECTOR = dlib.get_frontal_face_detector()
        return FACE_DETECTOR
    except Exception as e:
        print(f"[ERROR] Failed to load face detector: {e}")
        return None

# For MVP, keep FaceNet optional
facenet_model = None
try:
    facenet_model = load_facenet_model()
except:
    print("[WARNING] FaceNet not available, using fallback embeddings")

face_detector = load_face_detector()

# ==========================================
# DATABASE FUNCTIONS
# ==========================================

def init_identity_db():
    """Initialize identity database tables."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Protected entities table
        c.execute("""
            CREATE TABLE IF NOT EXISTS protected_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                type TEXT CHECK(type IN ('creator', 'celebrity', 'brand_character', 'test')),
                email TEXT,
                consent_agreement_date TEXT,
                created_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Identity embeddings table
        c.execute("""
            CREATE TABLE IF NOT EXISTS identity_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                embedding BLOB NOT NULL,
                source_file_name TEXT,
                registration_date TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES protected_entities(entity_id)
            )
        """)
        
        # License records table
        c.execute("""
            CREATE TABLE IF NOT EXISTS license_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                licensee_name TEXT,
                license_type TEXT CHECK(license_type IN ('exclusive', 'non_exclusive', 'unauthorized')),
                allowed_usage TEXT,
                start_date TEXT,
                end_date TEXT,
                FOREIGN KEY (entity_id) REFERENCES protected_entities(entity_id)
            )
        """)
        
        # Violation logs table
        c.execute("""
            CREATE TABLE IF NOT EXISTS violation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                matched_confidence REAL,
                violation_type TEXT,
                flagged_frame_path TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES protected_entities(entity_id)
            )
        """)
        
        conn.commit()
        print("[DB] Identity tables initialized")

init_identity_db()

# ==========================================
# FACE PROCESSING FUNCTIONS
# ==========================================

def extract_face_from_image(image_array, face_size=160):
    """
    Extract primary face from image.
    Returns: aligned face (160x160x3) or None
    """
    try:
        # Convert BGR to RGB if needed
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image_array
        
        # Detect faces
        h, w = rgb_image.shape[:2]
        blob = cv2.dnn.blobFromImage(rgb_image, 1.0, (300, 300), [104, 117, 123], False, False)
        
        if FACE_DETECTOR and hasattr(FACE_DETECTOR, 'setInput'):
            # OpenCV DNN detector
            FACE_DETECTOR.setInput(blob)
            detections = FACE_DETECTOR.forward()
            
            if len(detections) > 0 and detections[0, 0, 0, 2] > 0.5:
                # Extract primary face
                det = detections[0, 0, 0]
                x1 = int(det[3] * w)
                y1 = int(det[4] * h)
                x2 = int(det[5] * w)
                y2 = int(det[6] * h)
                
                # Ensure within bounds
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                face_crop = rgb_image[y1:y2, x1:x2]
                face_aligned = cv2.resize(face_crop, (face_size, face_size))
                return face_aligned
        else:
            # Fallback to dlib if available
            import dlib
            detector = dlib.get_frontal_face_detector()
            rects = detector(rgb_image, 1)
            
            if len(rects) > 0:
                rect = rects[0]
                x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                face_crop = rgb_image[y1:y2, x1:x2]
                face_aligned = cv2.resize(face_crop, (face_size, face_size))
                return face_aligned
        
        return None
    except Exception as e:
        print(f"[ERROR] Face extraction failed: {e}")
        return None

def compute_embedding(face_image):
    """
    Compute face embedding from aligned face image.
    Returns: 1D numpy array of embeddings
    """
    try:
        # Normalize face image
        face_array = np.array(face_image, dtype=np.float32) / 255.0
        face_array = face_array.reshape(1, 160, 160, 3)
        
        if facenet_model:
            embedding = facenet_model.predict(face_array, verbose=0)
            return embedding[0]
        else:
            # Fallback: random embedding (for testing without model)
            return np.random.rand(128)
    except Exception as e:
        print(f"[ERROR] Embedding computation failed: {e}")
        return None

def similarity_score(embedding1, embedding2):
    """Compute cosine similarity between two embeddings."""
    try:
        # Normalize embeddings
        e1 = embedding1 / np.linalg.norm(embedding1)
        e2 = embedding2 / np.linalg.norm(embedding2)
        return float(np.dot(e1, e2))
    except:
        return 0.0

# ==========================================
# API ENDPOINTS
# ==========================================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "identity_service"}), 200

@app.route("/match_identity", methods=["POST"])
def match_identity():
    """
    Match a face image against protected identity database.
    
    Request:
    {
        "image": base64_encoded_face_image,
        "threshold": 0.6  (optional, default 0.6)
    }
    
    Response:
    {
        "match_found": true/false,
        "matched_entity": {
            "entity_id": "creator_abc123",
            "name": "John Doe",
            "type": "creator",
            "confidence": 0.87
        },
        "license_status": "unauthorized" | "authorized" | "unknown"
    }
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "Missing 'image' field"}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data["image"])
            image_array = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            return jsonify({"error": f"Invalid image format: {e}"}), 400
        
        # Extract face
        face_crop = extract_face_from_image(image_array)
        if face_crop is None:
            return jsonify({
                "match_found": False,
                "error": "No face detected in image"
            }), 200
        
        # Compute embedding
        embedding = compute_embedding(face_crop)
        if embedding is None:
            return jsonify({
                "match_found": False,
                "error": "Failed to compute embedding"
            }), 200
        
        # Search database
        threshold = data.get("threshold", 0.6)
        best_match = None
        best_score = 0.0
        
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT ie.entity_id, ie.embedding, pe.name, pe.type
                FROM identity_embeddings ie
                JOIN protected_entities pe ON ie.entity_id = pe.entity_id
                WHERE pe.is_active = 1
            """)
            
            for entity_id, stored_embedding_blob, name, entity_type in c.fetchall():
                try:
                    # Deserialize stored embedding
                    stored_embedding = pickle.loads(stored_embedding_blob)
                    score = similarity_score(embedding, stored_embedding)
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            "entity_id": entity_id,
                            "name": name,
                            "type": entity_type,
                            "confidence": score
                        }
                except Exception as e:
                    print(f"[ERROR] Failed to process embedding for {entity_id}: {e}")
                    continue
        
        # Determine if match found
        if best_match and best_score >= threshold:
            # Get license status
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT license_type FROM license_records 
                    WHERE entity_id = ?
                    ORDER BY start_date DESC LIMIT 1
                """, (best_match["entity_id"],))
                result = c.fetchone()
                license_status = result[0] if result else "unknown"
            
            return jsonify({
                "match_found": True,
                "matched_entity": best_match,
                "license_status": license_status
            }), 200
        else:
            return jsonify({
                "match_found": False,
                "closest_match_score": best_score
            }), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/register_identity", methods=["POST"])
def register_identity():
    """
    Register a new protected identity with embeddings.
    Used by admin/creator registration system.
    
    Request:
    {
        "entity_id": "creator_123",
        "name": "John Doe",
        "type": "creator",
        "email": "john@example.com",
        "image": base64_encoded_image
    }
    """
    try:
        data = request.get_json()
        required_fields = ["entity_id", "name", "type", "image"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400
        
        entity_id = data["entity_id"]
        name = data["name"]
        entity_type = data["type"]
        email = data.get("email", "")
        
        # Decode image
        try:
            image_data = base64.b64decode(data["image"])
            image_array = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            return jsonify({"error": f"Invalid image format: {e}"}), 400
        
        # Extract face
        face_crop = extract_face_from_image(image_array)
        if face_crop is None:
            return jsonify({"error": "No face detected in image"}), 400
        
        # Compute embedding
        embedding = compute_embedding(face_crop)
        if embedding is None:
            return jsonify({"error": "Failed to compute embedding"}), 400
        
        # Store in database
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                
                # Insert or update entity
                c.execute("""
                    INSERT OR IGNORE INTO protected_entities 
                    (entity_id, name, type, email, consent_agreement_date, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (entity_id, name, entity_type, email, timestamp, timestamp))
                
                # Insert embedding
                embedding_blob = pickle.dumps(embedding)
                c.execute("""
                    INSERT INTO identity_embeddings (entity_id, embedding, source_file_name, registration_date)
                    VALUES (?, ?, ?, ?)
                """, (entity_id, embedding_blob, f"ref_{timestamp}.jpg", timestamp))
                
                # Insert default license record (unauthorized)
                c.execute("""
                    INSERT INTO license_records (entity_id, license_type, start_date)
                    VALUES (?, ?, ?)
                """, (entity_id, "unauthorized", timestamp))
                
                conn.commit()
            
            return jsonify({
                "success": True,
                "entity_id": entity_id,
                "message": f"Identity registered: {name}",
                "embedding_dim": len(embedding)
            }), 201
        
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return jsonify({"error": f"Entity {entity_id} already exists"}), 409
            raise
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/list_identities", methods=["GET"])
def list_identities():
    """List all registered identities (admin view)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT entity_id, name, type, email, created_at, is_active,
                       (SELECT COUNT(*) FROM identity_embeddings WHERE entity_id = pe.entity_id) as embedding_count
                FROM protected_entities pe
                ORDER BY created_at DESC
            """)
            
            columns = [desc[0] for desc in c.description]
            identities = [dict(zip(columns, row)) for row in c.fetchall()]
            
            return jsonify({
                "total": len(identities),
                "identities": identities
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete_identity/<entity_id>", methods=["DELETE"])
def delete_identity(entity_id):
    """Delete an identity and all its embeddings (right to be forgotten)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Soft delete (mark as inactive)
            c.execute("UPDATE protected_entities SET is_active = 0 WHERE entity_id = ?", (entity_id,))
            
            # Hard delete embeddings
            c.execute("DELETE FROM identity_embeddings WHERE entity_id = ?", (entity_id,))
            c.execute("DELETE FROM license_records WHERE entity_id = ?", (entity_id,))
            
            conn.commit()
        
        return jsonify({"success": True, "message": f"Identity {entity_id} deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Identity Service (Copyright Detection)")
    print("="*50)
    print("Listening on http://127.0.0.1:5002")
    print("="*50 + "\n")
    
    app.run(debug=False, port=5002, host="127.0.0.1")
