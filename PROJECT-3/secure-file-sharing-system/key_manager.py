from Crypto.Random import get_random_bytes
import sqlite3
import hashlib
from datetime import datetime, timedelta

class KeyManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS files
                         (id TEXT PRIMARY KEY,
                         key_salt BLOB NOT NULL,  # Combined key + salt
                         iv BLOB NOT NULL,
                         password_hash TEXT NOT NULL,
                         original_name TEXT NOT NULL,
                         expiry TIMESTAMP NOT NULL)''')
    
    def generate_keys(self, password):
        """Generate cryptographic materials with password derivation"""
        salt = get_random_bytes(16)
        key = self._derive_key(password, salt)
        iv = get_random_bytes(16)
        return key, iv, salt
    
    def _derive_key(self, password, salt):
        """Derive key from password using PBKDF2"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    def store_keys(self, file_id, key, salt, iv, password, original_name):
        """Store all encryption metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)",
                        (file_id,
                         salt + key,  # Store salt with key
                         iv,
                         hashlib.sha256(password.encode()).hexdigest(),
                         original_name,
                         datetime.now() + timedelta(days=1)))  # 24h expiry
    
    def retrieve_keys(self, file_id, password):
        """Retrieve keys if password matches"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key_salt, iv FROM files 
                WHERE id=? AND password_hash=? AND expiry > datetime('now')
            """, (file_id, hashlib.sha256(password.encode()).hexdigest()))
            
            row = cursor.fetchone()
            if row:
                key_salt = row[0]
                salt, key = key_salt[:16], key_salt[16:]  # Extract salt and key
                return key, row[1]  # key, iv
            return None, None
    
    def get_original_name(self, file_id):
        """Get original filename for download"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT original_name FROM files WHERE id=?", (file_id,))
            row = cursor.fetchone()
            return row[0] if row else "decrypted_file"
    
    def cleanup_expired(self):
        """Remove expired file entries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM files WHERE expiry <= datetime('now')")
