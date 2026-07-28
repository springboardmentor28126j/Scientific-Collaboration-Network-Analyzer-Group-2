import enum
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class ParticipationRole(str, enum.Enum):
    ATTENDEE = "attendee"
    PRESENTER = "presenter"
    ORGANIZER = "organizer"
    REVIEWER = "reviewer"


class ParticipationStatus(str, enum.Enum):
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    ATTENDED = "attended"


class ConferenceParticipation(Base):
    # Table was created by a teammate's migration as "conference_attendances";
    # this model builds on that existing table rather than a new one.
    __tablename__ = "conference_attendances"
    __table_args__ = (
        UniqueConstraint("conference_id", "researcher_id", name="uq_conference_researcher"),
    )
    # Nullable: added after the table already had rows, so older registrations
    # won't have a timestamp on record.
    registered_at: Mapped[Optional[str]] = mapped_column(
        DateTime, default=utcnow, nullable=True
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conferences.id"), nullable=False
    )
    researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )
    role: Mapped[ParticipationRole] = mapped_column(
        Enum(
            ParticipationRole,
            name="attendancerole",
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        default=ParticipationRole.ATTENDEE,
        nullable=False,
    )
    status: Mapped[ParticipationStatus] = mapped_column(
        Enum(
            ParticipationStatus,
            name="participationstatus",
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        default=ParticipationStatus.REGISTERED,
        nullable=False,
    )
    presentation_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    stored_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    researcher: Mapped["Researcher"] = relationship("Researcher")
    conference: Mapped["Conference"] = relationship("Conference", back_populates="attendances")