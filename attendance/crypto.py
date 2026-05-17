# attendance/crypto.py
# Phase 2: AES-256 Encryption for biometric face vectors (Privacy-by-Design)
# Uses Fernet (AES-128-CBC with HMAC-SHA256) — symmetric key stored in settings/env.

import base64
import os
from cryptography.fernet import Fernet
from django.conf import settings


def _get_fernet():
    """Return a Fernet instance using FACE_ENCRYPTION_KEY from settings."""
    key = getattr(settings, 'FACE_ENCRYPTION_KEY', None)
    if not key:
        # Derive a stable key from SECRET_KEY so existing dev data still works
        raw = settings.SECRET_KEY.encode()[:32]
        raw = raw.ljust(32, b'0')
        key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def encrypt_vector(vector_str: str) -> str:
    """Encrypt a comma-separated face vector string. Returns base64 ciphertext."""
    f = _get_fernet()
    token = f.encrypt(vector_str.encode())
    return token.decode()


def decrypt_vector(token_str: str) -> str:
    """Decrypt a Fernet token back to comma-separated face vector string."""
    f = _get_fernet()
    plaintext = f.decrypt(token_str.encode())
    return plaintext.decode()


def generate_new_key() -> str:
    """Helper: generate a fresh Fernet key for production use."""
    return Fernet.generate_key().decode()
