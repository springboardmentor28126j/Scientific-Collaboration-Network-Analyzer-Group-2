import enum
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, func, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ParticipationRole(str, enum.Enum):
    ATTENDEE = "attendee"
    PRESENTER = "presenter"
    ORGANIZER = "organizer"
    REVIEWER = "reviewer"


class SubmissionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PUBLISHED = "published"


class ConferenceStatus(str, enum.Enum):
    PLANNED = "planned"
    REGISTRATION_OPEN = "registration_open"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Conference(Base):
    __tablename__ = "conference"

    conference_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)

    organizing_institution_id: Mapped[int | None] = mapped_column(
        ForeignKey("institution.institution_id", ondelete="SET NULL"), nullable=True
    )
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ConferenceStatus] = mapped_column(
        Enum(ConferenceStatus), nullable=False, default=ConferenceStatus.PLANNED, server_default="PLANNED"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organizing_institution: Mapped["Institution"] = relationship()
    participations: Mapped[list["ConferenceParticipation"]] = relationship(
        back_populates="conference", cascade="all, delete-orphan"
    )


class ConferenceParticipation(Base):
    """
    Links a researcher to a conference with exactly one role. A researcher
    can only appear once per conference (enforced below) -- e.g. someone
    can't be both 'presenter' and 'reviewer' at the same conference in
    this model; pick the role that applies.
    """

    __tablename__ = "conference_participation"
    __table_args__ = (
        UniqueConstraint("conference_id", "researcher_id", name="uq_conference_researcher"),
    )

    participation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    conference_id: Mapped[int] = mapped_column(
        ForeignKey("conference.conference_id", ondelete="CASCADE"), nullable=False
    )
    researcher_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )

    role: Mapped[ParticipationRole] = mapped_column(Enum(ParticipationRole), nullable=False)
    submission_status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), nullable=False, default=SubmissionStatus.DRAFT, server_default="DRAFT"
    )

    presentation_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    publication_id: Mapped[int | None] = mapped_column(
        ForeignKey("publication.publication_id", ondelete="SET NULL"), nullable=True
    )

    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conference: Mapped["Conference"] = relationship(back_populates="participations")
    researcher: Mapped["ResearcherProfile"] = relationship()
    publication: Mapped["Publication"] = relationship()

    @property
    def researcher_name(self) -> str:
        return f"{self.researcher.first_name} {self.researcher.last_name}"
