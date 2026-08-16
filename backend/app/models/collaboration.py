import enum
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, Integer, func, ForeignKey, Enum, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CollaborationRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class CollaborationRequest(Base):
    """
    A LinkedIn-style "connect" invite between two researchers. This is
    deliberately a separate table from Collaboration: a request is a
    transient thing one researcher sends another and it disappears into
    accepted/rejected/cancelled, while a Collaboration (below) is the
    resulting durable network edge -- same split as Review (an invitation)
    vs. its target, or ConferenceParticipation.submission_status vs. the
    Conference itself.
    """
    __tablename__ = "collaboration_request"

    collaboration_request_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    requester_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    addressee_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )

    status: Mapped[CollaborationRequestStatus] = mapped_column(
        Enum(CollaborationRequestStatus), nullable=False,
        default=CollaborationRequestStatus.PENDING, server_default="PENDING",
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("requester_id != addressee_id", name="ck_collaboration_request_not_self"),
    )

    requester: Mapped["ResearcherProfile"] = relationship(foreign_keys=[requester_id])
    addressee: Mapped["ResearcherProfile"] = relationship(foreign_keys=[addressee_id])


class Collaboration(Base):
    """
    A durable, established connection between two researchers -- created the
    moment a CollaborationRequest is accepted. researcher1_id is always the
    smaller researcher_id of the pair (enforced in the repository, not the
    DB, the same way ConferenceParticipation/ProjectMember enforce their
    invariants at the application layer): this keeps the edge undirected and
    makes "does a collaboration already exist between A and B" a single
    lookup instead of two.

    strength / first_collaboration / last_collaboration are derived,
    denormalized metrics kept in sync from the researchers' shared
    publications (see collaboration_repository.recompute_metrics) rather
    than hand-maintained -- they're stored on the row instead of computed
    on every read because the network graph and "my collaborators" list
    need them for every edge at once, and recomputing that from
    publication/co-author joins on every page load doesn't scale.
    """
    __tablename__ = "collaboration"

    collaboration_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    researcher1_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    researcher2_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )

    # Count of shared publications backing this collaboration (see
    # collaboration_publication). Not a subjective "how close are they"
    # score -- just a simple, explainable co-authorship count.
    strength: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    first_collaboration: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_collaboration: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("researcher1_id", "researcher2_id", name="uq_collaboration_pair"),
        CheckConstraint("researcher1_id < researcher2_id", name="ck_collaboration_ordered_pair"),
    )

    researcher1: Mapped["ResearcherProfile"] = relationship(foreign_keys=[researcher1_id])
    researcher2: Mapped["ResearcherProfile"] = relationship(foreign_keys=[researcher2_id])
    shared_publications: Mapped[list["CollaborationPublication"]] = relationship(
        back_populates="collaboration", cascade="all, delete-orphan"
    )


class CollaborationPublication(Base):
    """Join table: which shared publications count toward a collaboration's strength."""

    __tablename__ = "collaboration_publication"
    __table_args__ = (
        UniqueConstraint("collaboration_id", "publication_id", name="uq_collaboration_publication"),
    )

    collaboration_publication_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    collaboration_id: Mapped[int] = mapped_column(
        ForeignKey("collaboration.collaboration_id", ondelete="CASCADE"), nullable=False
    )
    publication_id: Mapped[int] = mapped_column(
        ForeignKey("publication.publication_id", ondelete="CASCADE"), nullable=False
    )

    collaboration: Mapped["Collaboration"] = relationship(back_populates="shared_publications")
    publication: Mapped["Publication"] = relationship()
