from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class ConferenceSession(Base):
    """A single agenda item (talk/session) within a conference's schedule."""

    __tablename__ = "conference_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conferences.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    room: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Optional link to a registered presenter (a row in conference_attendances).
    speaker_participation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("conference_attendances.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(DateTime, default=utcnow, nullable=False)

    conference: Mapped["Conference"] = relationship("Conference", back_populates="sessions")
    speaker_participation: Mapped["ConferenceParticipation"] = relationship(
        "ConferenceParticipation"
    )