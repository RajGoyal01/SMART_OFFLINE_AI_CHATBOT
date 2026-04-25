from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt(message):
    try:
        return cipher.encrypt(message.encode()).decode()
    except:
        return "ENCRYPT_ERROR"

def decrypt(message):
    try:
        return cipher.decrypt(message.encode()).decode()
    except:
        return "DECRYPT_ERROR"