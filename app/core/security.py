import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class IssuedToken:
    """
    Bundles the encoded JWT with the two pieces of data the Redis session
    store needs (jti to key on, ttl_seconds to expire the session entry at
    the same moment the JWT itself would expire).
    """

    token: str
    jti: str
    ttl_seconds: int


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str, extra_claims: dict[str, Any] | None = None) -> IssuedToken:
    jti = str(uuid.uuid4())
    ttl_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expire = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    to_encode: dict[str, Any] = {"sub": subject, "role": role, "type": "access", "exp": expire, "jti": jti}
    if extra_claims:
        to_encode.update(extra_claims)
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return IssuedToken(token=token, jti=jti, ttl_seconds=ttl_seconds)


def create_refresh_token(subject: str) -> IssuedToken:
    jti = str(uuid.uuid4())
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    expire = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    to_encode = {"sub": subject, "type": "refresh", "exp": expire, "jti": jti}
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return IssuedToken(token=token, jti=jti, ttl_seconds=ttl_seconds)


def decode_token(token: str) -> dict[str, Any]:
    """
    Raises jose.JWTError if the token is invalid or expired.
    Callers are expected to catch this and translate it into a 401 response.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
