"""
Database Setup & Test Data Generator
Run this to initialize the identity database with test data.
"""

import sqlite3
import os
import numpy as np
import pickle
from datetime import datetime

DB_PATH = "database.db"

def init_db():
    """Initialize database with schema."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Protected entities
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
        
        # Identity embeddings
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
        
        # License records
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
        
        # Violation logs
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
        print("[DB] Schema initialized")

def add_test_identity(entity_id, name, entity_type="test", embedding_dim=128):
    """
    Add a test identity with random embedding.
    For MVP testing without real face images.
    """
    timestamp = datetime.now().isoformat()
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Check if already exists
            c.execute("SELECT COUNT(*) FROM protected_entities WHERE entity_id = ?", (entity_id,))
            if c.fetchone()[0] > 0:
                print(f"[SKIP] {name} already exists")
                return
            
            # Generate random embedding (for testing)
            embedding = np.random.randn(embedding_dim).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)  # Normalize
            
            # Insert entity
            c.execute("""
                INSERT INTO protected_entities 
                (entity_id, name, type, email, consent_agreement_date, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (entity_id, name, entity_type, f"{entity_id}@test.com", timestamp, timestamp))
            
            # Insert embedding
            embedding_blob = pickle.dumps(embedding)
            c.execute("""
                INSERT INTO identity_embeddings (entity_id, embedding, source_file_name, registration_date)
                VALUES (?, ?, ?, ?)
            """, (entity_id, embedding_blob, "test_reference.jpg", timestamp))
            
            # Insert default license (unauthorized)
            c.execute("""
                INSERT INTO license_records (entity_id, license_type, start_date)
                VALUES (?, ?, ?)
            """, (entity_id, "unauthorized", timestamp))
            
            conn.commit()
            print(f"[OK] Added test identity: {name} ({entity_id})")
    
    except Exception as e:
        print(f"[ERROR] Failed to add {name}: {e}")

def list_identities():
    """List all registered identities."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT entity_id, name, type, created_at, is_active
                FROM protected_entities
                ORDER BY created_at DESC
            """)
            
            print("\n" + "="*60)
            print("Registered Identities")
            print("="*60)
            for entity_id, name, entity_type, created_at, is_active in c.fetchall():
                status = "✓ Active" if is_active else "✗ Inactive"
                print(f"{status} | {name:20} | {entity_id:20} | {entity_type}")
            print("="*60 + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to list identities: {e}")

def clear_all():
    """WARNING: Clear all data. Use only for testing."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM violation_logs")
            c.execute("DELETE FROM license_records")
            c.execute("DELETE FROM identity_embeddings")
            c.execute("DELETE FROM protected_entities")
            conn.commit()
        print("[OK] All data cleared")
    except Exception as e:
        print(f"[ERROR] Failed to clear: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Identity Database Setup")
    print("="*60 + "\n")
    
    # Initialize schema
    init_db()
    
    # Add test identities
    print("\nAdding test identities...")
    add_test_identity("creator_001", "Abubakkar Khan", "creator")
    add_test_identity("creator_002", "John Doe", "creator")
    add_test_identity("creator_003", "Jane Smith", "creator")
    add_test_identity("celebrity_001", "Elon Musk", "celebrity")
    add_test_identity("celebrity_002", "Taylor Swift", "celebrity")
    
    # List all
    list_identities()
    
    print("[OK] Database setup complete!")
    print("\nNext steps:")
    print("1. Start identity service: python identity_service.py")
    print("2. Go to http://127.0.0.1:5002/list_identities to verify")
    print("3. Integrate with main app.py (Phase 3)")
