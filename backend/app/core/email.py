"""A single helper every route calls to send an outbound email via SMTP.
Deliberately best-effort, same contract as app/core/audit.py::log_audit
and app/core/notifications.py::create_notification -- an email failure
(bad credentials, SMTP server down, no SMTP configured at all) must never
break the request that triggered it. Callers should fire-and-forget this;
it never raises.
"""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("app.email")


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends a plain-text email. Returns True if it was sent (or at least
    handed off to the SMTP server without error), False otherwise --
    callers can log the return value but should never let it affect the
    HTTP response, since email delivery is inherently best-effort."""
    if not settings.SMTP_HOST:
        # No SMTP configured (typical for local dev) -- print the full
        # email to the console instead of silently dropping it, so links
        # embedded in the body (password reset, email verification, etc.)
        # are still usable without needing to query the DB directly.
        logger.warning(
            "SMTP_HOST not configured -- would have sent email to %s\n"
            "Subject: %s\n"
            "---\n%s\n---",
            to_email,
            subject,
            body,
        )
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False
