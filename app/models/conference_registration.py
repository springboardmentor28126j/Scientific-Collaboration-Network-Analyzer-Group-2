import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base_model import TimestampMixin


class ConferenceRegistration(TimestampMixin, Base):
    __tablename__ = "conference_registrations"

    __table_args__ = (
        UniqueConstraint(
            "conference_id",
            "user_id",
            name="uq_conference_user",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    conference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conferences.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    conference = relationship(
        "Conference",
        back_populates="registrations",
    )

    user = relationship(
        "User",
        back_populates="conference_registrations",
    )
