"""
Sends transactional emails via fastapi-mail.

In development, MAIL_SERVER points at the `mailcatcher` container (SMTP on
1025) so every email sent here is viewable at http://localhost:1080
instead of hitting a real inbox. In production, these same settings point
at a real SMTP provider — nothing in this module changes between envs.
"""

from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
    TEMPLATE_FOLDER=TEMPLATES_DIR,
)

fast_mail = FastMail(conf)


class EmailService:
    @staticmethod
    async def send_institution_verification_email(to_email: str, name: str, link: str) -> None:
        message = MessageSchema(
            subject="Verify your institution account",
            recipients=[to_email],
            template_body={"name": name, "verification_link": link},
            subtype=MessageType.html,
        )
        await fast_mail.send_message(message, template_name="verify_email.html")

    @staticmethod
    async def send_invite_verification_email(
        to_email: str, name: str, institution_name: str, role: str, link: str
    ) -> None:
        message = MessageSchema(
            subject=f"You've been invited to join {institution_name}",
            recipients=[to_email],
            template_body={
                "name": name,
                "institution_name": institution_name,
                "role": role,
                "verification_link": link,
            },
            subtype=MessageType.html,
        )
        await fast_mail.send_message(message, template_name="verify_invite.html")

    @staticmethod
    async def send_password_reset_email(to_email: str, name: str, link: str) -> None:
        message = MessageSchema(
            subject="Reset your password",
            recipients=[to_email],
            template_body={"name": name, "reset_link": link},
            subtype=MessageType.html,
        )
        await fast_mail.send_message(message, template_name="reset_password.html")
