from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
from jose import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Native bcrypt hashing (No Passlib bug, 72 bytes safe)."""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Native bcrypt verification."""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """JWT Access Token create karta hai."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any] | None:
    """JWT Token ko verify aur decode karta hai."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except Exception:
        return None