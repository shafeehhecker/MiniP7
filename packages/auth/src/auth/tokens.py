"""JWT access tokens (Milestone 1 — auth commons).

Signed, expiring tokens that carry the user's id. The API validates these on
every protected route and derives the current user from them, replacing the
temporary X-User-Id header. Pure functions; the signing secret is injected by the
caller (the API reads it from the environment) so this module stays config-free
and testable.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

import jwt

ALGORITHM = "HS256"
DEFAULT_EXPIRY_MINUTES = 60 * 24  # 24h


class TokenError(Exception):
    """Raised when a token is missing, expired, tampered with, or invalid."""


def create_access_token(user_id: str, secret: str,
                        expires_minutes: int = DEFAULT_EXPIRY_MINUTES) -> str:
    if not secret:
        raise ValueError("A signing secret is required.")
    now = _dt.datetime.now(_dt.timezone.utc)
    payload: dict[str, Any] = {
        "sub": user_id,
        "iat": now,
        "exp": now + _dt.timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_access_token(token: str, secret: str) -> str:
    """Return the user id from a valid token, else raise TokenError."""
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenError("Token has expired.")
    except jwt.InvalidTokenError:
        raise TokenError("Invalid token.")
    sub = payload.get("sub")
    if not sub:
        raise TokenError("Token missing subject.")
    return sub
