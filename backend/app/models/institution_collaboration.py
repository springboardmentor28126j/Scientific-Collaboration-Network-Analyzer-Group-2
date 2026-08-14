import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class InstitutionCollaborationStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ENDED = "ended"


class InstitutionCollaboration(Base):
    """A formal collaboration between two institutions (distinct from
    Collaboration in collaboration.py, which tracks researcher-to-researcher
    edges). Mirrors the institution_collaborations table added by
    alembic/versions/0023_institution_collaborations.py (revision id
    '0022_institution_collaborations')."""

    __tablename__ = "institution_collaborations"
    __table_args__ = (
        CheckConstraint("institution1_id != institution2_id", name="ck_institution_collab_not_self"),
        UniqueConstraint("institution1_id", "institution2_id", name="uq_institution_collab_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    institution1_id: Mapped[int] = mapped_column(Integer, ForeignKey("institutions.id"), nullable=False)
    institution2_id: Mapped[int] = mapped_column(Integer, ForeignKey("institutions.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[InstitutionCollaborationStatus] = mapped_column(
        Enum(
            InstitutionCollaborationStatus,
            name="institutioncollaborationstatus",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=InstitutionCollaborationStatus.PENDING,
        nullable=False,
    )
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    institution1: Mapped["Institution"] = relationship("Institution", foreign_keys=[institution1_id])
    institution2: Mapped["Institution"] = relationship("Institution", foreign_keys=[institution2_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
