import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.review_assignment import ReviewAssignment


class ReviewDecision(StrEnum):
    ACCEPT = "ACCEPT"
    MINOR_REVISION = "MINOR_REVISION"
    MAJOR_REVISION = "MAJOR_REVISION"
    REJECT = "REJECT"


class Review(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Stores a review submitted by an assigned reviewer.

    Each review belongs to exactly one ReviewAssignment.
    """

    __tablename__ = "reviews"

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("review_assignments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    decision: Mapped[ReviewDecision] = mapped_column(
        Enum(ReviewDecision, name="review_decision"),
        nullable=False,
    )

    score: Mapped[int] = mapped_column(nullable=False)

    strengths: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    weaknesses: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    comments: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    assignment: Mapped["ReviewAssignment"] = relationship(
        "ReviewAssignment",
        back_populates="review",
    )
