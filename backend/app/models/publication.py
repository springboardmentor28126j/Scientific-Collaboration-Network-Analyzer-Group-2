import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class PublicationStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PublicationType(str, enum.Enum):
    JOURNAL_PAPER = "journal_paper"
    CONFERENCE_PAPER = "conference_paper"
    BOOK = "book"
    PATENT = "patent"
    TECHNICAL_REPORT = "technical_report"


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    doi_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional["PublicationType"]] = mapped_column(
        Enum(
            PublicationType,
            name="publicationtype",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=True,
    )
    stored_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[PublicationStatus] = mapped_column(
        Enum(
            PublicationStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=PublicationStatus.DRAFT,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    # Set when a reviewer approves/rejects a 'submitted' publication. Authors
    # can no longer set status to 'published' themselves (see the
    # /review endpoint in api/routes/publications.py).
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    review_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    authors: Mapped[list["PublicationAuthor"]] = relationship(
        "PublicationAuthor", back_populates="publication", cascade="all, delete-orphan"
    )


class PublicationAuthor(Base):
    __tablename__ = "publication_authors"
    __table_args__ = (
        UniqueConstraint("publication_id", "researcher_id", name="uq_publication_researcher"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    publication_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("publications.id"), nullable=False
    )
    researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )

    publication: Mapped["Publication"] = relationship("Publication", back_populates="authors")
    researcher: Mapped["Researcher"] = relationship("Researcher")

    @property
    def email(self) -> str | None:
        """The author's email, via researcher -> user. Relies on the caller
        having eager-loaded researcher and researcher.user (see
        api/routes/publications.py); returns None rather than lazy-loading
        if they aren't, so this never becomes its own N+1 source."""
        if self.researcher is not None and self.researcher.user is not None:
            return self.researcher.user.email
        return None
