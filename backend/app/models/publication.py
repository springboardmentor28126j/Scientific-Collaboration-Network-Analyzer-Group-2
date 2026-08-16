import enum
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, func, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PublicationType(str, enum.Enum):
    JOURNAL_PAPER = "journal_paper"
    CONFERENCE_PAPER = "conference_paper"
    BOOK = "book"
    PATENT = "patent"
    TECHNICAL_REPORT = "technical_report"
    OTHER = "other"


class PublicationStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Publication(Base):
    __tablename__ = "publication"

    publication_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)

    publication_type: Mapped[PublicationType] = mapped_column(Enum(PublicationType), nullable=False)
    status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus), nullable=False, default=PublicationStatus.DRAFT, server_default="DRAFT"
    )

    primary_author_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    institution_id: Mapped[int | None] = mapped_column(
        ForeignKey("institution.institution_id", ondelete="SET NULL"), nullable=True
    )

    venue_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    primary_author: Mapped["ResearcherProfile"] = relationship()
    institution: Mapped["Institution"] = relationship()
    co_authors: Mapped[list["PublicationAuthor"]] = relationship(
        back_populates="publication", cascade="all, delete-orphan"
    )

    @property
    def co_author_ids(self) -> list[int]:
        return [ca.researcher_id for ca in sorted(self.co_authors, key=lambda ca: ca.author_order)]


class PublicationAuthor(Base):
    """Co-authorship: many researchers can be linked to one publication."""

    __tablename__ = "publication_author"
    __table_args__ = (UniqueConstraint("publication_id", "researcher_id", name="uq_publication_author"),)

    publication_author_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    publication_id: Mapped[int] = mapped_column(
        ForeignKey("publication.publication_id", ondelete="CASCADE"), nullable=False
    )
    researcher_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    author_order: Mapped[int] = mapped_column(default=1, server_default="1")

    publication: Mapped["Publication"] = relationship(back_populates="co_authors")
    researcher: Mapped["ResearcherProfile"] = relationship()
