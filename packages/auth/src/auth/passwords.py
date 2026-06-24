"""Password hashing (Phase / Milestone 1 — auth commons).

Isolated, pure functions. Passwords are hashed with bcrypt; the plaintext is
never stored or logged. This module is the *only* place hashing happens, so the
security-sensitive code is auditable in one spot (ADR-0006).
"""
from __future__ import annotations

import bcrypt


def hash_password(plaintext: str) -> str:
    """Return a bcrypt hash of the password. Safe to store."""
    if not plaintext:
        raise ValueError("Password must not be empty.")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plaintext.encode("utf-8"), salt).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    """Check a plaintext against a stored hash. Constant-time via bcrypt."""
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
