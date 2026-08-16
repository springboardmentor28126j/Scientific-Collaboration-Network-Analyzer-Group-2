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

import logging

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

_ACCESS_PREFIX = "session:access:"
_REFRESH_PREFIX = "session:refresh:"
_LOGIN_FAIL_PREFIX = "login:fail:"


def _safe_set(key: str, ttl_seconds: int, value: str) -> None:
    try:
        redis_client.setex(key, ttl_seconds, value)
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis unavailable while creating session: %s", exc)


def create_access_session(jti: str, user_id: int, ttl_seconds: int) -> None:
    """Registers a newly issued access token as an active session."""
    _safe_set(f"{_ACCESS_PREFIX}{jti}", ttl_seconds, str(user_id))


def create_refresh_session(jti: str, user_id: int, ttl_seconds: int) -> None:
    """Registers a newly issued refresh token as an active session."""
    _safe_set(f"{_REFRESH_PREFIX}{jti}", ttl_seconds, str(user_id))


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


def _login_fail_key(email: str) -> str:
    # Case-insensitive, same normalization the DB lookup uses for emails.
    return f"{_LOGIN_FAIL_PREFIX}{email.strip().lower()}"


def record_failed_login(email: str, window_seconds: int) -> int:
    """
    Increments the failed-attempt counter for an email and (re)starts its
    expiry window on every failure, so `window_seconds` of no further
    failures is what it takes for the counter to clear on its own -- a
    sliding lockout window rather than a fixed one.

    Fails open (returns 0) if Redis is unavailable: brute-force throttling
    is a defense-in-depth layer on top of real password checks, and it
    should never be able to block legitimate logins by breaking.
    """
    key = _login_fail_key(email)
    try:
        count = redis_client.incr(key)
        redis_client.expire(key, window_seconds)
        return count
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis unavailable while recording failed login: %s", exc)
        return 0


def get_failed_login_count(email: str) -> int:
    try:
        value = redis_client.get(_login_fail_key(email))
        return int(value) if value is not None else 0
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis unavailable while reading failed login count: %s", exc)
        return 0


def reset_failed_login(email: str) -> None:
    """Clears the failed-attempt counter, e.g. after a successful login."""
    try:
        redis_client.delete(_login_fail_key(email))
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis unavailable while resetting failed login count: %s", exc)


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
