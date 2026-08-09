from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class Conversation(Base):
    """A message thread is always scoped to exactly one project OR one
    collaboration -- never both, never neither. There's no 'create
    conversation' endpoint; one is lazily created the first time someone
    opens messages for that project/collaboration."""

    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("project_id", name="uq_conversation_project"),
        UniqueConstraint("collaboration_id", name="uq_conversation_collaboration"),
        CheckConstraint(
            "(project_id IS NOT NULL AND collaboration_id IS NULL) OR "
            "(project_id IS NULL AND collaboration_id IS NOT NULL)",
            name="ck_conversation_exactly_one_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )
    collaboration_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("collaborations.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    project: Mapped[Optional["Project"]] = relationship("Project")
    collaboration: Mapped[Optional["Collaboration"]] = relationship("Collaboration")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    sender_researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    sender: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[sender_researcher_id])


class ConversationRead(Base):
    """Tracks, per researcher per conversation, the timestamp of the last
    message they've seen -- used only to compute unread counts."""

    __tablename__ = "conversation_reads"
    __table_args__ = (
        UniqueConstraint("conversation_id", "researcher_id", name="uq_conversation_read"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False
    )
    last_read_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)