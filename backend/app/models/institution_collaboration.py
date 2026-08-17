import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class InstitutionCollaborationStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ENDED = "ended"


class InstitutionCollaboration(Base):
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
        Enum(InstitutionCollaborationStatus, values_callable=lambda e: [m.value for m in e]),
        default=InstitutionCollaborationStatus.PENDING,
        nullable=False,
    )
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    institution1: Mapped["Institution"] = relationship("Institution", foreign_keys=[institution1_id])
    institution2: Mapped["Institution"] = relationship("Institution", foreign_keys=[institution2_id])