import base64
import numpy as np
from django.conf import settings

_fernet = None

def get_fernet():
    global _fernet
    if _fernet is None:
        try:
            from cryptography.fernet import Fernet
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if key:
                if isinstance(key, str):
                    key = key.encode()
                _fernet = Fernet(key)
        except Exception:
            pass
    return _fernet

def encrypt_embedding(embedding_array: np.ndarray) -> str:
    """Encrypt numpy array for export/backup. Returns base64 string."""
    f = get_fernet()
    if f is None:
        return base64.b64encode(embedding_array.astype(np.float32).tobytes()).decode()
    raw_bytes = embedding_array.astype(np.float32).tobytes()
    encrypted = f.encrypt(raw_bytes)
    return base64.b64encode(encrypted).decode()

def decrypt_embedding(encrypted_str: str) -> np.ndarray:
    """Decrypt to numpy array."""
    f = get_fernet()
    raw = base64.b64decode(encrypted_str.encode())
    if f is None:
        return np.frombuffer(raw, dtype=np.float32)
    decrypted = f.decrypt(raw)
    return np.frombuffer(decrypted, dtype=np.float32)
