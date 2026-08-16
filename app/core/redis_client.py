"""
Redis-backed session store.

Why this exists:
JWTs are stateless by design, which means a "logout" can't normally invalidate
a token before it naturally expires. To satisfy the spec's requirement for a
refresh-token blacklist *and* a session cache with a single mechanism, every
access/refresh token we issue gets a matching Redis key (an "allowlist" entry)
with a TTL equal to the token's remaining lifetime:

    session:access:{jti}  -> user_id   (TTL = ACCESS_TOKEN_EXPIRE_MINUTES)
    session:refresh:{jti} -> user_id   (TTL = REFRESH_TOKEN_EXPIRE_DAYS)

A token is only accepted if its Redis entry still exists. Logging out, or
rotating a refresh token, simply deletes the entry -- the token becomes
worthless immediately, without us needing to track a separate "revoked list"
that grows without bound. Redis's own TTL expiry cleans up naturally for
tokens that just expire on their own.
"""

import redis

from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

_ACCESS_PREFIX = "session:access:"
_REFRESH_PREFIX = "session:refresh:"


def create_access_session(jti: str, user_id: int, ttl_seconds: int) -> None:
    """Registers a newly issued access token as an active session."""
    redis_client.setex(f"{_ACCESS_PREFIX}{jti}", ttl_seconds, str(user_id))


def create_refresh_session(jti: str, user_id: int, ttl_seconds: int) -> None:
    """Registers a newly issued refresh token as an active session."""
    redis_client.setex(f"{_REFRESH_PREFIX}{jti}", ttl_seconds, str(user_id))


def is_access_session_active(jti: str) -> bool:
    return redis_client.exists(f"{_ACCESS_PREFIX}{jti}") == 1


def is_refresh_session_active(jti: str) -> bool:
    return redis_client.exists(f"{_REFRESH_PREFIX}{jti}") == 1


def revoke_access_session(jti: str) -> None:
    """Effectively 'logs out' an access token immediately, ahead of its natural expiry."""
    redis_client.delete(f"{_ACCESS_PREFIX}{jti}")


def revoke_refresh_session(jti: str) -> None:
    """Invalidates a refresh token -- used on logout and on every refresh (rotation)."""
    redis_client.delete(f"{_REFRESH_PREFIX}{jti}")


def revoke_all_sessions_for_user(user_id: int) -> None:
    """
    Best-effort revocation of every active session for a user (e.g. on password
    change or admin-forced logout). Uses SCAN rather than KEYS to avoid blocking
    Redis on large keyspaces.
    """
    for prefix in (_ACCESS_PREFIX, _REFRESH_PREFIX):
        for key in redis_client.scan_iter(match=f"{prefix}*"):
            if redis_client.get(key) == str(user_id):
                redis_client.delete(key)
