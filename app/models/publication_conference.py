import uuid
from datetime import date, datetime, timezone
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConferenceOutcome(StrEnum):
    PRESENTED = "PRESENTED"
    PUBLISHED_IN_PROCEEDINGS = "PUBLISHED_IN_PROCEEDINGS"
    BEST_PAPER = "BEST_PAPER"
    HONORABLE_MENTION = "HONORABLE_MENTION"
    CANCELLED = "CANCELLED"


class PublicationConference(Base):
    __tablename__ = "publication_conferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    conference_name: Mapped[str] = mapped_column(String(255))
    venue: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))

    conference_date: Mapped[date] = mapped_column(Date)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    proceedings_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    isbn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issn: Mapped[str | None] = mapped_column(String(50), nullable=True)

    outcome: Mapped[ConferenceOutcome] = mapped_column(
        Enum(ConferenceOutcome, name="conference_outcome")
    )

    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    publication = relationship(
        "Publication",
        back_populates="conference",
    )

    creator = relationship(
        "User",
    )
