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

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="publications",
    )

    authors: Mapped[list["PublicationAuthor"]] = relationship(
        "PublicationAuthor",
        back_populates="publication",
        cascade="all, delete-orphan",
    )
