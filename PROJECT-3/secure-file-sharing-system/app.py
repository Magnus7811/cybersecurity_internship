import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import sqlite3
import hashlib
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Random secret key
app.config['KEY_DB'] = 'keys.db'

# Initialize Key Manager
class KeyManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS files
                         (id TEXT PRIMARY KEY,
                         key_salt BLOB NOT NULL,
                         iv BLOB NOT NULL,
                         password_hash TEXT NOT NULL,
                         original_name TEXT NOT NULL,
                         expiry TIMESTAMP NOT NULL)''')
    
    def generate_keys(self, password):
        salt = get_random_bytes(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        iv = get_random_bytes(16)
        return key, iv, salt
    
    def store_keys(self, file_id, key, salt, iv, password, original_name):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)",
                       (file_id,
                        salt + key,
                        iv,
                        hashlib.sha256(password.encode()).hexdigest(),
                        original_name,
                        datetime.now() + timedelta(days=1)))
    
    def retrieve_keys(self, file_id, password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key_salt, iv FROM files 
                WHERE id=? AND password_hash=? AND expiry > datetime('now')
            """, (file_id, hashlib.sha256(password.encode()).hexdigest()))
            row = cursor.fetchone()
            if row:
                key_salt = row[0]
                return key_salt[16:], row[1]  # Returns (key, iv)
            return None, None
    
    def get_original_name(self, file_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT original_name FROM files WHERE id=?", (file_id,))
            row = cursor.fetchone()
            return row[0] if row else "decrypted_file"
    
    def cleanup_expired(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM files WHERE expiry <= datetime('now')")

key_manager = KeyManager(app.config['KEY_DB'])

# Encryption/Decryption Functions
def encrypt_file(file_path, key, iv):
    output_path = file_path + '.enc'
    
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    
    with open(output_path, 'wb') as f:
        f.write(ciphertext)
    
    return output_path

def decrypt_file(file_path, key, iv):
    output_path = file_path.replace('.enc', '')
    
    with open(file_path, 'rb') as f:
        ciphertext = f.read()
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    with open(output_path, 'wb') as f:
        f.write(plaintext)
    
    return output_path

# Routes
@app.route('/')
def index():
    key_manager.cleanup_expired()  # Clean expired files on home page load
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    password = request.form.get('password')
    
    if not password or len(password) < 4:
        flash('Password must be at least 4 characters', 'error')
        return redirect(url_for('index'))
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    try:
        # Generate cryptographic materials
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Generate keys with password
        key, iv, salt = key_manager.generate_keys(password)
        
        # Encrypt the file
        encrypted_path = encrypt_file(filepath, key, iv)
        file_id = os.path.basename(encrypted_path)
        
        # Store all metadata
        key_manager.store_keys(
            file_id=file_id,
            key=key,
            salt=salt,
            iv=iv,
            password=password,
            original_name=filename
        )
        
        # Cleanup original file
        os.unlink(filepath)
        
        # Generate shareable link
        share_url = f"{request.url_root}download/{file_id}"
        return render_template('share.html', 
                            share_url=share_url,
                            filename=filename)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<file_id>', methods=['GET', 'POST'])
def download_file(file_id):
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    
    if not os.path.exists(encrypted_path):
        return render_template('error.html', error="File not found"), 404
    
    if request.method == 'POST':
        password = request.form.get('password')
        key, iv = key_manager.retrieve_keys(file_id, password)
        
        if key and iv:
            decrypted_path = decrypt_file(encrypted_path, key, iv)
            original_name = key_manager.get_original_name(file_id)
            
            response = send_file(
                decrypted_path,
                as_attachment=True,
                download_name=original_name
            )
            
            # Cleanup decrypted file
            os.unlink(decrypted_path)
            return response
        
        return render_template('password.html', 
                           file_id=file_id,
                           error="Invalid password or expired link")
    
    return render_template('password.html', file_id=file_id)

# Startup
if __name__ == "__main__":
    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Generate SSL certificates if they don't exist
    if not all([os.path.exists('localhost.pem'), os.path.exists('localhost-key.pem')]):
        os.system('openssl req -x509 -newkey rsa:4096 -nodes -out localhost.pem -keyout localhost-key.pem -days 365 -subj "/CN=localhost"')
    
    # Run the app with HTTPS
    app.run(
        ssl_context=('localhost.pem', 'localhost-key.pem'),
        port=5000,
        debug=True
    )
