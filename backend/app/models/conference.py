import enum
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow

class ConferenceType(str, enum.Enum):
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    HYBRID = "hybrid"

class Conference(Base):
    __tablename__ = "conferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    website_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, default=utcnow, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    conference_type: Mapped[Optional[ConferenceType]] = mapped_column(
        Enum(
            ConferenceType,
            name="conferencetype",
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=True,
    )
    # Nullable: added after the table already had rows. New conferences are
    # required (by the API layer) to set this so a conference always belongs
    # to the institution that's hosting it.
    institution_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("institutions.id"), nullable=True
    )
    attendances: Mapped[list["ConferenceParticipation"]] = relationship(
        "ConferenceParticipation", back_populates="conference", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["ConferenceSession"]] = relationship(
        "ConferenceSession", back_populates="conference", cascade="all, delete-orphan"
    )