import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.publication import Publication
    from app.models.user import User
    from app.models.review import Review


class ReviewAssignmentStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class ReviewAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents the assignment of a reviewer to a publication.

    A publication may have multiple reviewers.
    A reviewer may review multiple publications.
    """

    __tablename__ = "review_assignments"

    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publications.id", ondelete="CASCADE"),
        nullable=False,
    )

    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    assigned_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[ReviewAssignmentStatus] = mapped_column(
        String(20),
        default=ReviewAssignmentStatus.PENDING,
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    publication: Mapped["Publication"] = relationship(
        "Publication",
        back_populates="review_assignments",
    )

    reviewer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reviewer_id],
        back_populates="review_assignments",
    )

    assigned_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[assigned_by],
    )
    review: Mapped["Review | None"] = relationship(
        "Review",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )
