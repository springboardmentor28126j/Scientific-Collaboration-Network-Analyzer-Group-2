from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class Notification(Base):
    """An in-app notification for a user. Rows are inserted by
    create_notification() (see app/core/notifications.py) and read back
    via GET /notifications for the current user.

    Column shape matches the real 'notifications' table already present
    in the shared DB (created by an external migration chain sharing this
    project's local Postgres instance -- see check_notifications.py
    diagnostic): recipient_user_id (not user_id) and link (not link_url),
    with no title/entity_type/entity_id columns at all. Adopted as-is
    rather than altering that table. The Python-side attribute names
    below (user_id, link_url) are kept for readability/consistency with
    the rest of this codebase (AuditLog.user_id, etc.) via column-name
    aliasing -- only the DB column names differ.
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # The recipient -- who this notification is for.
    user_id: Mapped[int] = mapped_column(
        "recipient_user_id", Integer, ForeignKey("users.id"), nullable=False
    )

    # Short machine-readable kind, e.g. "collaboration_request_received".
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    # The only text field the real table has -- no separate title. Kept
    # under 500 chars to match the real column's VARCHAR(500) limit (see
    # MAX_MESSAGE_LENGTH in app/core/notifications.py, which truncates).
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    # Where "View" should take the user, e.g. "/collaborations".
    link_url: Mapped[Optional[str]] = mapped_column("link", String(255), nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    user: Mapped["User"] = relationship("User")
