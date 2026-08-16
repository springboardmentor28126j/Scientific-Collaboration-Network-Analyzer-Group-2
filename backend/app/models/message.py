from datetime import datetime

from sqlalchemy import Text, Boolean, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Message(Base):
    """
    A private chat message, always scoped to a Collaboration -- there is no
    way to message a researcher you don't already have an established
    Collaboration with. collaboration_id is the conversation; there's no
    separate Conversation entity because Collaboration already uniquely
    identifies "these two people" (its own uq_collaboration_pair
    constraint guarantees at most one edge per pair).
    """
    __tablename__ = "message"

    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    collaboration_id: Mapped[int] = mapped_column(
        ForeignKey("collaboration.collaboration_id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_message_collaboration_created", "collaboration_id", "created_at"),
    )

    collaboration: Mapped["Collaboration"] = relationship()
    sender: Mapped["ResearcherProfile"] = relationship()