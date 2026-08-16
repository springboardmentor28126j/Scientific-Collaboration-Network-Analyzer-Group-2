import enum
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReviewTargetType(str, enum.Enum):
    PUBLICATION = "publication"
    CONFERENCE_SUBMISSION = "conference_submission"


class ReviewStatus(str, enum.Enum):
    ASSIGNED = "assigned"      # invited, awaiting the reviewer's accept/decline
    ACCEPTED = "accepted"      # reviewer accepted, review in progress
    DECLINED = "declined"      # reviewer declined the invitation
    COMPLETED = "completed"    # score/comments/recommendation submitted


class ReviewRecommendation(str, enum.Enum):
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"


class Review(Base):
    """
    A single reviewer's evaluation of one publication or conference
    submission. Deliberately references its target with (target_type,
    target_id) rather than two nullable FKs -- same pattern as AuditLog --
    since a review always points at exactly one of Publication or
    ConferenceParticipation, never both.

    Note: this is advisory. Completing a review does not itself change the
    Publication/submission status -- the organizing institution admin (or
    system admin) makes the final accept/reject call using that recommendation
    as input (BR conference flow: "Reviewer Reviews -> Institution Admin
    (optional) -> System Admin (optional) -> Accepted").
    """
    __tablename__ = "review"

    review_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    target_type: Mapped[ReviewTargetType] = mapped_column(Enum(ReviewTargetType), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)

    reviewer_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    assigned_by: Mapped[int | None] = mapped_column(ForeignKey("user.user_id", ondelete="SET NULL"), nullable=True)

    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), nullable=False, default=ReviewStatus.ASSIGNED, server_default="ASSIGNED"
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[ReviewRecommendation | None] = mapped_column(Enum(ReviewRecommendation), nullable=True)

    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reviewer: Mapped["User"] = relationship(foreign_keys=[reviewer_id])
    assigned_by_user: Mapped["User"] = relationship(foreign_keys=[assigned_by])
