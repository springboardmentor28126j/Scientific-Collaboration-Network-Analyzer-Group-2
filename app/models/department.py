import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base_model import TimestampMixin


class Department(TimestampMixin, Base):

    __tablename__ = "departments"

    __table_args__ = (
        UniqueConstraint(
            "institution_id",
            "name",
            name="uq_department_per_institution",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    institution = relationship(
        "Institution",
        back_populates="departments",
    )


    researchers = relationship(
    	"Researcher",
    	secondary="researcher_departments",
    	back_populates="departments",
    )
