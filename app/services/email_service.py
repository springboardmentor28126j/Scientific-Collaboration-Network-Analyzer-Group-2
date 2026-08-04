import secrets
import smtplib

from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


class EmailService:

    @staticmethod
    def generate_verification_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def verification_expiry() -> datetime:
        return datetime.utcnow() + timedelta(minutes=30)

    @staticmethod
    def generate_reset_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def reset_token_expiry() -> datetime:
        return datetime.utcnow() + timedelta(minutes=15)

    @staticmethod
    def send_email(
        recipient: str,
        subject: str,
        html_content: str,
    ):
        message = MIMEMultipart("alternative")

        message["Subject"] = subject
        message["From"] = settings.MAIL_FROM
        message["To"] = recipient

        message.attach(
            MIMEText(
                html_content,
                "html",
            )
        )

        try:
            with smtplib.SMTP(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
            ) as server:

                server.starttls()

                server.login(
                    settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD,
                )

                server.sendmail(
                    settings.MAIL_FROM,
                    recipient,
                    message.as_string(),
                )

            print(f"Email sent successfully to {recipient}")

        except Exception as e:
            print(f"Failed to send email: {e}")
            raise

    @staticmethod
    def send_verification_email(
        email: str,
        token: str,
    ):
        verification_link = (
            f"{settings.FRONTEND_URL}/verify-email?token={token}"
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>

        <body style="font-family:Arial,sans-serif;background:#f4f6f8;padding:40px;">

            <div style="
                max-width:600px;
                margin:auto;
                background:white;
                border-radius:10px;
                padding:40px;
                box-shadow:0 2px 10px rgba(0,0,0,.1);
            ">

                <h2 style="color:#0d6efd;">
                    Scientific Collaboration Network Analyzer
                </h2>

                <p>Hello,</p>

                <p>
                    Thank you for registering.
                </p>

                <p>
                    Please verify your email address by clicking the button below.
                </p>

                <p style="text-align:center;margin:40px 0;">

                    <a
                        href="{verification_link}"
                        style="
                            background:#0d6efd;
                            color:white;
                            text-decoration:none;
                            padding:14px 28px;
                            border-radius:6px;
                            display:inline-block;
                            font-weight:bold;
                        "
                    >
                        Verify Email
                    </a>

                </p>

                <p>
                    This verification link will expire in
                    <strong>30 minutes</strong>.
                </p>

                <p>
                    If you did not create this account,
                    you can safely ignore this email.
                </p>

                <hr>

                <small style="color:gray;">
                    Scientific Collaboration Network Analyzer
                </small>

            </div>

        </body>
        </html>
        """
        EmailService.send_email(
            recipient=email,
            subject="Verify Your Email Address",
            html_content=html,
        )

    @staticmethod
    def send_reset_password_email(
        email: str,
        token: str,
    ):
        reset_link = (
            f"{settings.FRONTEND_URL}/reset-password?token={token}"
        )

        html = f"""
        <!DOCTYPE html>
        <html>

        <body style="font-family:Arial;background:#f4f6f8;padding:40px;">

            <div style="
                max-width:600px;
                margin:auto;
                background:white;
                padding:40px;
                border-radius:10px;
                box-shadow:0 2px 10px rgba(0,0,0,.1);
            ">

                <h2 style="color:#dc3545;">
                    Password Reset
                </h2>

                <p>
                    We received a request to reset your password.
                </p>

                <p style="text-align:center;margin:40px 0;">

                    <a
                        href="{reset_link}"
                        style="
                            background:#dc3545;
                            color:white;
                            padding:14px 28px;
                            border-radius:6px;
                            text-decoration:none;
                            font-weight:bold;
                        "
                    >
                        Reset Password
                    </a>

                </p>

                <p>
                    This link expires in
                    <strong>15 minutes</strong>.
                </p>

                <p>
                    If you didn't request a password reset,
                    simply ignore this email.
                </p>

                <hr>

                <small style="color:gray;">
                    Scientific Collaboration Network Analyzer
                </small>

            </div>

        </body>
        </html>
        """

        EmailService.send_email(
            recipient=email,
            subject="Reset Your Password",
            html_content=html,
        )
