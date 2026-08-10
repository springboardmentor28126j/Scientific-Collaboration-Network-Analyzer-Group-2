"""A single helper every route calls to record an in-app Notification row.
Deliberately best-effort (same pattern as app/core/audit.py::log_audit):
a notification failure must never break the request that triggered it, so
any exception here is swallowed after rolling back just this insert.
"""
from sqlalchemy.orm import Session

from app.models.notification import Notification

# The real 'notifications.message' column is VARCHAR(500) -- truncate
# rather than let a long message raise a DB error and get silently
# swallowed by the try/except below (better to show a clipped message
# than none at all).
MAX_MESSAGE_LENGTH = 500


def create_notification(
    db: Session,
    *,
    user_id: int,
    type: str,
    message: str,
    link_url: str | None = None,
) -> None:
    try:
        db.add(
            Notification(
                user_id=user_id,
                type=type,
                message=message[:MAX_MESSAGE_LENGTH],
                link_url=link_url,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
