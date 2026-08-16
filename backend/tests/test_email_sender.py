import logging

from app.core import email_sender


def test_send_verification_email_skips_when_disabled(monkeypatch, caplog):
    original_enabled = email_sender.settings.EMAIL_VERIFICATION_ENABLED
    email_sender.settings.EMAIL_VERIFICATION_ENABLED = False

    class DummySMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            pass

        def login(self, *args, **kwargs):
            pass

        def sendmail(self, *args, **kwargs):
            pass

    monkeypatch.setattr(email_sender.smtplib, "SMTP", DummySMTP)

    try:
        with caplog.at_level(logging.INFO):
            email_sender.send_verification_email(
                "user@example.com",
                "http://localhost:5000/verify-email?token=test-token",
            )
    finally:
        email_sender.settings.EMAIL_VERIFICATION_ENABLED = original_enabled

    assert "disabled" in caplog.text.lower()


def test_send_verification_email_warns_when_smtp_unconfigured(caplog):
    original_username = email_sender.settings.SMTP_USERNAME
    original_password = email_sender.settings.SMTP_PASSWORD

    email_sender.settings.SMTP_USERNAME = ""
    email_sender.settings.SMTP_PASSWORD = ""

    try:
        with caplog.at_level(logging.WARNING):
            email_sender.send_verification_email(
                "user@example.com",
                "http://localhost:5000/verify-email?token=test-token",
            )
    finally:
        email_sender.settings.SMTP_USERNAME = original_username
        email_sender.settings.SMTP_PASSWORD = original_password

    assert "SMTP not configured" in caplog.text
    assert "Set SMTP_USERNAME and SMTP_PASSWORD" in caplog.text
    assert "http://localhost:5000/verify-email?token=test-token" in caplog.text
