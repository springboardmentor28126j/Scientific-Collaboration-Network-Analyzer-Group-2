import uuid
from sqlalchemy.orm import relationship
from datetime import date
from sqlalchemy import String, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.base_model import TimestampMixin


class Conference(TimestampMixin, Base):
    __tablename__ = "conferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    conference_date: Mapped[date | None] = mapped_column(Date,nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrations = relationship("ConferenceRegistration",back_populates="conference",cascade="all, delete-orphan",)
