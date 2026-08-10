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


class CollaborationRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class CollaborationRequest(Base):
    """A 'connect' invite between two researchers. Kept separate from
    Collaboration: a request is transient (it resolves into
    accepted/rejected/cancelled), while a Collaboration is the durable
    network edge created once a request is accepted."""

    __tablename__ = "collaboration_requests"
    __table_args__ = (
        CheckConstraint("requester_id != addressee_id", name="ck_collaboration_request_not_self"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )
    addressee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )
    status: Mapped[CollaborationRequestStatus] = mapped_column(
        Enum(
            CollaborationRequestStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=CollaborationRequestStatus.PENDING,
        nullable=False,
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    requester: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[requester_id])
    addressee: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[addressee_id])


class Collaboration(Base):
    """A durable, established connection between two researchers, created
    when a CollaborationRequest is accepted. researcher1_id is always the
    smaller researchers.id of the pair (enforced in the route layer, not
    just the DB check constraint) so 'does an edge exist between A and B'
    is a single lookup instead of two.

    strength / first_collaboration / last_collaboration are derived from
    the researchers' shared publications (see recompute_collaboration_metrics
    in api/routes/collaborations.py) rather than hand-maintained.
    """

    __tablename__ = "collaborations"
    __table_args__ = (
        UniqueConstraint("researcher1_id", "researcher2_id", name="uq_collaboration_pair"),
        CheckConstraint("researcher1_id < researcher2_id", name="ck_collaboration_ordered_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    researcher1_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )
    researcher2_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )
    strength: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    first_collaboration: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_collaboration: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    researcher1: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[researcher1_id])
    researcher2: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[researcher2_id])
    shared_publications: Mapped[list["CollaborationPublication"]] = relationship(
        "CollaborationPublication", back_populates="collaboration", cascade="all, delete-orphan"
    )


class CollaborationPublication(Base):
    """Join table: which shared publications count toward a collaboration's strength."""

    __tablename__ = "collaboration_publications"
    __table_args__ = (
        UniqueConstraint(
            "collaboration_id", "publication_id", name="uq_collaboration_publication"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    collaboration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collaborations.id"), nullable=False
    )
    publication_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("publications.id"), nullable=False
    )

    collaboration: Mapped["Collaboration"] = relationship(
        "Collaboration", back_populates="shared_publications"
    )
    publication: Mapped["Publication"] = relationship("Publication")
