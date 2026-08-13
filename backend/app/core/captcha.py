"""Server-side verification for the reCAPTCHA v2 checkbox on the login
page. Unlike app/core/email.py and app/core/notifications.py (both
deliberately best-effort -- swallow errors so a side-effect failure never
breaks the request), this is a security control: a *configured* captcha
check must fail closed. If Google says the token is invalid/expired, or
the verification request itself errors out, the login attempt is denied.

The one place this mirrors the best-effort pattern is when
RECAPTCHA_SECRET_KEY is unset entirely -- that's treated as "captcha
disabled for local dev" (same idea as SMTP_HOST being blank in
email.py), and login proceeds without a captcha check, with a clear
warning logged so it's obvious this isn't happening silently.

Uses urllib (stdlib) rather than adding a new HTTP client dependency --
this backend doesn't otherwise depend on requests/httpx.
"""
import json
import logging
import urllib.parse
import urllib.request

from app.core.config import settings

logger = logging.getLogger("app.captcha")

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def verify_recaptcha(token: str | None) -> bool:
    """Returns True if the reCAPTCHA checkbox was completed and Google
    confirms the token is valid. Returns False (deny) for a missing
    token, an invalid/expired token, or any error talking to Google --
    except when RECAPTCHA_SECRET_KEY isn't configured at all, in which
    case verification is skipped and this returns True."""
    if not settings.RECAPTCHA_SECRET_KEY:
        logger.warning(
            "RECAPTCHA_SECRET_KEY not configured -- skipping captcha "
            "verification (captcha effectively disabled)"
        )
        return True

    if not token:
        return False

    data = urllib.parse.urlencode(
        {"secret": settings.RECAPTCHA_SECRET_KEY, "response": token}
    ).encode("utf-8")

    try:
        request = urllib.request.Request(VERIFY_URL, data=data, method="POST")
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
        return bool(result.get("success"))
    except Exception:
        logger.exception("Failed to verify reCAPTCHA token with Google")
        return False
