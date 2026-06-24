"""Tests for the auth commons — hashing and JWT."""
import time
import pytest
from auth import (hash_password, verify_password,
                  create_access_token, decode_access_token, TokenError)

SECRET = "test-secret"


def test_hash_is_not_plaintext_and_verifies():
    h = hash_password("hunter2pass")
    assert h != "hunter2pass"
    assert verify_password("hunter2pass", h)


def test_wrong_password_fails():
    h = hash_password("correct-horse")
    assert not verify_password("battery-staple", h)


def test_verify_handles_garbage_without_raising():
    assert verify_password("x", "not-a-valid-hash") is False


def test_empty_password_rejected():
    with pytest.raises(ValueError):
        hash_password("")


def test_token_round_trip():
    tok = create_access_token("user_123", SECRET)
    assert decode_access_token(tok, SECRET) == "user_123"


def test_token_wrong_secret_rejected():
    tok = create_access_token("user_123", SECRET)
    with pytest.raises(TokenError):
        decode_access_token(tok, "different-secret")


def test_tampered_token_rejected():
    tok = create_access_token("user_123", SECRET)
    with pytest.raises(TokenError):
        decode_access_token(tok + "x", SECRET)


def test_expired_token_rejected():
    tok = create_access_token("user_123", SECRET, expires_minutes=-1)
    with pytest.raises(TokenError):
        decode_access_token(tok, SECRET)
