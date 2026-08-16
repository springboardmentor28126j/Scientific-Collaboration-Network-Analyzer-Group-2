import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str, text_body: str | None = None) -> None:
    """
    Sends a single email via SMTP. Raises on failure -- callers decide
    whether that should fail the request or just be logged, since
    "verification email didn't send" shouldn't necessarily break registration.
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        # Dev-mode fallback: log instead of failing outright when SMTP
        # isn't configured yet, so the rest of the flow stays testable.
        logger.warning(
            "SMTP not configured (SMTP_USERNAME/SMTP_PASSWORD empty). "
            "Set SMTP_USERNAME and SMTP_PASSWORD in backend/.env to send real verification emails. "
            "Would have sent email to %s: %s\n%s",
            to_email, subject, html_body,
        )
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email

    if text_body:
        message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    # SMTP_TIMEOUT: without this, an unreachable or slow mail server (a
    # firewall silently dropping the connection, Gmail rate-limiting, a
    # misconfigured host) blocks this call indefinitely -- and since every
    # caller of this (via notify()) treats email as best-effort inside a
    # try/except, that only catches exceptions, not a hang. A bounded
    # timeout is what actually makes "best-effort" mean "never blocks the
    # request," not just "swallow errors."
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT_SECONDS) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())

    logger.info("Sent email to %s: %s", to_email, subject)


def send_notification_email(to_email: str, subject: str, message: str, link_url: str | None = None) -> None:
    """
    Generic email for whichever in-app notification types are also worth
    an email -- see EMAIL_ENABLED_NOTIF_TYPES in app/utils/notifications.py
    for which ones and why. Deliberately reuses the same title/message text
    already written for the in-app notification instead of maintaining a
    second copy of the wording per event type: one branded shell, many
    event types plugged into it, so adding a 6th/20th email type later is a
    one-line registry entry, not a new function.
    """
    cta_html = (
        f'<p style="margin-top:18px;">'
        f'<a href="{link_url}" style="display:inline-block;padding:10px 18px;'
        f'background:#3457D5;color:#ffffff;text-decoration:none;border-radius:6px;font-size:14px;">'
        f'View in SCNA</a></p>'
        if link_url else ""
    )
    html_body = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;max-width:480px;">
      <p style="font-size:15px;color:#1C2541;line-height:1.5;">{message}</p>
      {cta_html}
      <p style="font-size:12px;color:#888888;margin-top:28px;border-top:1px solid #eeeeee;padding-top:12px;">
        You're receiving this because email notifications are enabled for this event on your SCNA account.
      </p>
    </div>
    """
    text_body = message + (f"\n\nView it here: {link_url}" if link_url else "")
    send_email(to_email, subject, html_body, text_body)


def send_verification_email(to_email: str, verification_link: str) -> None:
    if not settings.EMAIL_VERIFICATION_ENABLED:
        # Lets an environment (or a specific rollout stage) turn verification
        # emails off entirely -- e.g. local/dev setups that don't want to
        # configure SMTP just to exercise registration -- without touching
        # the SMTP_USERNAME/PASSWORD dev-fallback path, which is meant for
        # "not configured yet" rather than "intentionally disabled".
        logger.info(
            "Email verification is disabled (EMAIL_VERIFICATION_ENABLED=False); "
            "skipping verification email to %s",
            to_email,
        )
        return

    subject = "Verify your email — Scientific Collaboration Network Analyzer"
    html_body = f"""
    <p>Welcome! Please confirm your email address to activate your account.</p>
    <p><a href="{verification_link}">Click here to verify your email</a></p>
    <p>Or copy and paste this link into your browser:</p>
    <p>{verification_link}</p>
    <p>This link expires in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours.</p>
    """
    text_body = (
        f"Welcome! Please confirm your email address to activate your account.\n\n"
        f"Verify here: {verification_link}\n\n"
        f"This link expires in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours."
    )
    send_email(to_email, subject, html_body, text_body)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    subject = "Reset your password — Scientific Collaboration Network Analyzer"
    html_body = f"""
    <p>We received a request to reset the password for this account.</p>
    <p><a href="{reset_link}">Click here to choose a new password</a></p>
    <p>Or copy and paste this link into your browser:</p>
    <p>{reset_link}</p>
    <p>This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
    <p>If you didn't request this, you can safely ignore this email — your password won't be changed.</p>
    """
    text_body = (
        f"We received a request to reset the password for this account.\n\n"
        f"Reset it here: {reset_link}\n\n"
        f"This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.\n\n"
        f"If you didn't request this, you can safely ignore this email — your password won't be changed."
    )
    send_email(to_email, subject, html_body, text_body)


def send_password_reset_unavailable_email(to_email: str) -> None:
    """
    Sent instead of a reset link when a forgot-password request comes in for
    an account that signs in with Google and has no local password to reset.
    Telling the *account owner* this via email is fine; it's only the
    anonymous forgot-password API response that must stay silent either way.
    """
    subject = "Password reset request — Scientific Collaboration Network Analyzer"
    html_body = """
    <p>We received a request to reset the password for this account.</p>
    <p>This account signs in with Google and doesn't have a password to reset.
    Please use the "Sign in with Google" button on the login page instead.</p>
    <p>If you didn't request this, you can safely ignore this email.</p>
    """
    text_body = (
        "We received a request to reset the password for this account.\n\n"
        "This account signs in with Google and doesn't have a password to reset. "
        "Please use the \"Sign in with Google\" button on the login page instead.\n\n"
        "If you didn't request this, you can safely ignore this email."
    )
    send_email(to_email, subject, html_body, text_body)