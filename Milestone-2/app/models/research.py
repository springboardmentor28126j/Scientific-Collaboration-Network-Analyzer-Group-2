import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ResearcherProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "researcher_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    department: Mapped[str | None] = mapped_column(String(255))
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    research_interests: Mapped[list[str]] = mapped_column(JSON, default=list)
    affiliations: Mapped[list[str]] = mapped_column(JSON, default=list)


class Publication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "publications"

    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    abstract: Mapped[str | None] = mapped_column(Text)
    publication_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    doi: Mapped[str | None] = mapped_column(String(255), unique=True)
    published_on: Mapped[date | None] = mapped_column(Date)
    file_url: Mapped[str | None] = mapped_column(String(1000))


class PublicationAuthor(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "publication_authors"
    __table_args__ = (UniqueConstraint("publication_id", "user_id", name="uq_publication_author"),)

    publication_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    author_order: Mapped[int] = mapped_column(Integer, default=1)


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    funding_source: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)


class ProjectMember(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(100), default="MEMBER")


class Conference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conferences"

    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    website_url: Mapped[str | None] = mapped_column(String(1000))


class ConferenceParticipation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conference_participations"
    __table_args__ = (UniqueConstraint("conference_id", "user_id", name="uq_conference_participant"),)

    conference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conferences.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    presentation_title: Mapped[str | None] = mapped_column(String(500))
    participation_type: Mapped[str] = mapped_column(String(40), default="ATTENDEE")


class ConferenceEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conference_events"

    conference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conferences.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    description: Mapped[str | None] = mapped_column(Text)


class Citation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "citations"

    source_publication_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"), index=True)
    cited_publication_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"), index=True)


class InstitutionalCollaboration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "institutional_collaborations"

    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), index=True)
    partner_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(255))
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[str] = mapped_column(String(100))


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    link: Mapped[str | None] = mapped_column(String(1000))
