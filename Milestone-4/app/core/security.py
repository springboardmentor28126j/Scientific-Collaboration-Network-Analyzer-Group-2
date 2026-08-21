"""
Password hashing and JWT creation/verification.

Two kinds of tokens flow through this module:
  1. Session JWTs (access + refresh) — used for authenticated API calls.
  2. Purpose-built "action" tokens (email verify / invite verify / password
     reset) — short random strings stored (hashed) in the DB and emailed as
     links. These are generated in app/services/*, not here; this module
     only handles JWTs and password hashing.
"""

import secrets
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str) -> str:
    return _create_token(
        user_id, TokenType.ACCESS, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        user_id, TokenType.REFRESH, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """Returns the decoded payload, or None if the token is invalid/expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def generate_raw_action_token() -> str:
    """
    A cryptographically random, URL-safe token for one-off action links
    (email verification, invite verification, password reset).

    The raw value is what gets emailed to the user; only its hash is
    stored in the DB (see hash_action_token), same principle as password
    storage — if the DB leaks, the tokens in it are useless.
    """
    return secrets.token_urlsafe(32)


def hash_action_token(raw_token: str) -> str:
    return pwd_context.hash(raw_token)


def verify_action_token(raw_token: str, hashed_token: str) -> bool:
    return pwd_context.verify(raw_token, hashed_token)
