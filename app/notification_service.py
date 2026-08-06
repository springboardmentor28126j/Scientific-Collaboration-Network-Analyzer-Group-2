"""Create in-app notifications and optionally deliver the same event by Resend."""
import json
import os
from urllib import request

from sqlalchemy.orm import Session

from app import models


def is_resend_configured() -> bool:
    return bool(os.getenv("RESEND_API_KEY") and os.getenv("RESEND_FROM_EMAIL"))


def _send_resend_email(recipient: str, subject: str, message: str, link: str | None) -> bool:
    """Return False when email is intentionally not configured or delivery fails."""
    api_key = os.getenv("RESEND_API_KEY")
    sender = os.getenv("RESEND_FROM_EMAIL")
    if not api_key or not sender:
        return False

    app_url = os.getenv("APP_URL", "http://127.0.0.1:5173")
    action = f'<p><a href="{app_url}/{link}">Open Scientific Collaboration Network Analyzer</a></p>' if link else ""
    payload = json.dumps({
        "from": sender,
        "to": [recipient],
        "subject": subject,
        "html": f"<h2>{subject}</h2><p>{message}</p>{action}",
    }).encode("utf-8")
    email_request = request.Request(
        "https://api.resend.com/emails", data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST"
    )
    try:
        with request.urlopen(email_request, timeout=10) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def notify_users(db: Session, users: list[models.User], *, notification_type: str, title: str, message: str, link: str | None = None, email: bool = True) -> int:
    """Store one notification per recipient, then email the event when Resend is configured."""
    notifications = [models.Notification(user_id=user.id, type=notification_type, title=title, message=message, link=link) for user in users]
    db.add_all(notifications)
    db.commit()

    if not email:
        return 0
    accepted = 0
    for user, notification in zip(users, notifications):
        if _send_resend_email(user.email, title, message, link):
            notification.email_sent = 1
            accepted += 1
    db.commit()
    return accepted


def notify_all_users(db: Session, **kwargs) -> int:
    return notify_users(db, db.query(models.User).all(), **kwargs)


def email_recipients(recipients: list[str], *, title: str, message: str, link: str | None) -> int:
    """Send an announcement to saved researcher contact emails without creating a login notification."""
    return sum(_send_resend_email(email, title, message, link) for email in set(recipients) if email)
