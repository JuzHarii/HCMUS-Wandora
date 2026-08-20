from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Any

import bcrypt
import jwt

from .config import get_settings


def generate_token() -> str:
    """Tạo token ngẫu nhiên cho các luồng xác thực hoặc chia sẻ."""
    return secrets.token_urlsafe(32)


def hash_value(value: str) -> str:
    """Băm một giá trị văn bản để lưu trữ an toàn hơn."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu khớp với hash bằng bcrypt."""
    try:
        pw_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Băm mật khẩu bằng bcrypt."""
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Tạo JWT access token."""
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Giải mã và kiểm tra tính hợp lệ của JWT token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.PyJWTError:
        return None
