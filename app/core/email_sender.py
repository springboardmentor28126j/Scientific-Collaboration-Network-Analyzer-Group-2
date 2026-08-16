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

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())

    logger.info("Sent email to %s: %s", to_email, subject)


def send_verification_email(to_email: str, verification_link: str) -> None:
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
