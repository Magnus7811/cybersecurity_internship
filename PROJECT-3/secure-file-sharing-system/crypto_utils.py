from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os

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
