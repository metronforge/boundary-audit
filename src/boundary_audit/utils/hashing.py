"""Deterministic SHA-256 helpers."""

import hashlib


def sha256_hex(payload: bytes) -> str:
    """Return the lowercase SHA-256 digest of bytes."""
    return hashlib.sha256(payload).hexdigest()
