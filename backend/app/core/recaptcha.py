"""
Google reCAPTCHA v2 verification for the login brute-force guard.

Once too many failed login attempts have piled up for an email, the login
form renders a Google reCAPTCHA widget and the frontend submits the token
it produces (the "g-recaptcha-response") alongside the credentials. This
module verifies that token server-side against Google's siteverify API
before the password is even checked again.

Unlike the arithmetic CAPTCHA this replaces, there's no server-issued
challenge to store: Google owns the challenge/response lifecycle, and this
module only needs to check the token Google's widget produced.
"""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
_REQUEST_TIMEOUT_SECONDS = 8


def verify_recaptcha(token: str | None, remote_ip: str | None = None) -> bool:
    """
    Verifies a reCAPTCHA response token against Google's siteverify API.
    Fails closed: a missing token, an unreachable Google endpoint, or a
    verification failure are all treated as a failed CAPTCHA, since this
    check exists specifically to block automated login attempts.
    """
    if not token:
        return False

    if not settings.RECAPTCHA_SECRET_KEY:
        logger.warning("RECAPTCHA_SECRET_KEY is not configured; failing closed.")
        return False

    payload = {"secret": settings.RECAPTCHA_SECRET_KEY, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        resp = httpx.post(_VERIFY_URL, data=payload, timeout=_REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        result = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("reCAPTCHA verification request failed: %s", exc)
        return False

    if not result.get("success"):
        logger.info("reCAPTCHA verification failed: %s", result.get("error-codes"))
        return False

    return True
