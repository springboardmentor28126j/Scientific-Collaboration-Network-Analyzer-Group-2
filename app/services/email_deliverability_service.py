"""
Real-time email deliverability pre-check, using ZeroBounce.

This is deliberately separate from the email_verification_token flow.
That flow is the *authoritative* proof a mailbox is real (the user actually
clicked a link sent to it). This service is just fast, best-effort UX
feedback during registration to catch obvious typos/fake addresses before
the user even submits the form -- it should never be the only thing
standing between a fake email and account creation, and it fails open
(doesn't block registration) if the API key isn't configured or the
third-party service is unreachable.
"""
import logging

import httpx

from app.core.config import settings
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)

_CACHE_PREFIX = "email_deliverability:"

# ZeroBounce statuses that mean "this mailbox is genuinely usable".
# "catch-all" and "unknown" are deliberately treated as inconclusive, not
# invalid -- they mean ZeroBounce couldn't fully confirm it, not that it's
# fake, so we shouldn't scare a legitimate user over those.
_VALID_STATUSES = {"valid"}
_INVALID_STATUSES = {"invalid", "spamtrap", "abuse", "do_not_mail"}


def check_email_deliverability(email: str) -> dict:
    """
    Returns {"checked": bool, "is_valid": bool | None, "reason": str | None}.

    checked=False means we couldn't actually verify (no API key configured,
    provider errored, or the result was inconclusive) -- the frontend should
    treat this as "unknown, don't block," not as "invalid."
    """
    email = email.strip().lower()

    if not settings.ZEROBOUNCE_API_KEY:
        logger.info("ZEROBOUNCE_API_KEY not configured; skipping deliverability check for %s", email)
        return {"checked": False, "is_valid": None, "reason": "Deliverability check not configured"}

    cache_key = f"{_CACHE_PREFIX}{email}"
    try:
        cached = redis_client.get(cache_key)
        if cached is not None:
            return {"checked": True, "is_valid": cached == "true", "reason": None}
    except Exception as exc:
        logger.warning("Redis unavailable for deliverability cache check: %s", exc)

    try:
        response = httpx.get(
            "https://api.zerobounce.net/v2/validate",
            params={"api_key": settings.ZEROBOUNCE_API_KEY, "email": email},
            timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()
        zb_status = data.get("status")

        if zb_status in _VALID_STATUSES:
            result = {"checked": True, "is_valid": True, "reason": None}
        elif zb_status in _INVALID_STATUSES:
            result = {"checked": True, "is_valid": False, "reason": "Mailbox does not appear to exist"}
        else:
            # catch-all / unknown / do_not_mail-adjacent -- inconclusive, fail open.
            logger.info("ZeroBounce inconclusive status '%s' for %s", zb_status, email)
            return {"checked": False, "is_valid": None, "reason": None}

        try:
            redis_client.setex(
                cache_key,
                settings.EMAIL_DELIVERABILITY_CACHE_TTL_SECONDS,
                "true" if result["is_valid"] else "false",
            )
        except Exception as exc:
            logger.warning("Redis unavailable for deliverability cache write: %s", exc)

        return result

    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("ZeroBounce deliverability check failed for %s: %s", email, exc)
        return {"checked": False, "is_valid": None, "reason": "Deliverability service unavailable"}