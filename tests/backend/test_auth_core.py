"""Unit checks for password and token behavior used by account authentication."""

import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.schemas.auth import SignUpRequest


def test_password_hash_never_equals_the_password():
    password = "SecurePass!123"
    encoded = hash_password(password)
    assert encoded != password
    assert verify_password(password, encoded)
    assert not verify_password("WrongPass!123", encoded)


def test_access_token_round_trip_contains_the_user_subject():
    token = create_access_token("user-123")
    assert decode_access_token(token) == "user-123"


def test_invalid_token_is_rejected():
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("not-a-jwt")
    assert exc_info.value.status_code == 401


def test_sign_up_requires_a_strong_password():
    with pytest.raises(ValueError):
        SignUpRequest(full_name="Test User", email="test@example.com", password="short")


def test_sign_up_normalizes_name_and_email():
    payload = SignUpRequest(full_name="  Test   User  ", email="TEST@EXAMPLE.COM", password="SecurePass!123")
    assert payload.full_name == "Test User"
    assert payload.email == "test@example.com"
