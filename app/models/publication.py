import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.publication_author import PublicationAuthor
    from app.models.review_assignment import ReviewAssignment
    from app.models.publication_history import PublicationHistory
    from app.models.institution import Institution
    from app.models.publication_reference import PublicationReference
    from app.models.notification import Notification


class PublicationStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class PublicationType(StrEnum):
    JOURNAL = "JOURNAL"
    CONFERENCE = "CONFERENCE"
    BOOK = "BOOK"
    PATENT = "PATENT"
    TECHNICAL_REPORT = "TECHNICAL_REPORT"


class Publication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Stores the core information about a research publication.

    This model only represents the publication itself.

    Co-authors, reviews, citations, versions and history are stored in
    their own tables.
    """

    __tablename__ = "publications"

    title: Mapped[str] = mapped_column(String(500), nullable=False)

    abstract: Mapped[str] = mapped_column(Text, nullable=False)

    publication_type: Mapped[PublicationType] = mapped_column(
        Enum(PublicationType, name="publication_type"),
        nullable=False,
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus, name="publication_status"),
        default=PublicationStatus.DRAFT,
        nullable=False,
    )

    doi: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    pdf_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    pdf_public_id: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    editor_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decision_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="publications",
    )

    institution: Mapped["Institution"] = relationship(
        "Institution",
        back_populates="publications",
    )

    authors: Mapped[list["PublicationAuthor"]] = relationship(
        "PublicationAuthor",
        back_populates="publication",
        cascade="all, delete-orphan",
    )

    review_assignments: Mapped[list["ReviewAssignment"]] = relationship(
        "ReviewAssignment",
        back_populates="publication",
        cascade="all, delete-orphan",
    )

    editor: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[decided_by],
        back_populates="editor_decisions",
    )

    history: Mapped[list["PublicationHistory"]] = relationship(
        "PublicationHistory",
        back_populates="publication",
        cascade="all, delete-orphan",
        order_by="PublicationHistory.created_at.desc()",
    )

    conference = relationship(
        "PublicationConference",
        back_populates="publication",
        uselist=False,
        cascade="all, delete-orphan",
    )

    references: Mapped[list["PublicationReference"]] = relationship(
        "PublicationReference",
        back_populates="publication",
        cascade="all, delete-orphan",
        order_by="PublicationReference.reference_order",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="publication",
    )
