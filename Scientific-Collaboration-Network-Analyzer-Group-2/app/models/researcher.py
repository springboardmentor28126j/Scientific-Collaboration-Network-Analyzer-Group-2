import uuid

from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import TimestampMixin
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped

from app.db.database import Base


class Researcher(TimestampMixin, Base):
    __tablename__ = "researchers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id"),
        nullable=False,
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id"),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    bio: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    experience: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    orcid: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
    )

    google_scholar: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    research_gate: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    linkedin: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="researcher",
    )

    institution = relationship(
        "Institution",
        back_populates="researchers",
    )

    department = relationship(
        "Department",
        back_populates="researchers",
    )
