from datetime import datetime

from sqlalchemy import String, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Notification(Base):
    """
    In-app notification for a single user. notif_type is a plain string
    (e.g. "review_assigned", "affiliation_approved") rather than a Postgres
    enum on purpose -- this list is expected to keep growing as new features
    ship, and altering a Postgres enum type is disruptive (see the
    publicationstatus migration, which needed a special non-transactional
    migration just to add two values). A free-text type with an index is a
    much cheaper way to keep extending this.
    """
    __tablename__ = "notification"

    notification_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, index=True)

    notif_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    link_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user: Mapped["User"] = relationship()
