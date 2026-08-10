from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class ReviewerAssignment(Base):
    """Grants a Reviewer permission to approve/reject submitted publications.

    Scoped in one of two ways (exactly one must be set):
      - institution_id: the reviewer may review any publication whose
        author belongs to this institution.
      - publication_id: the reviewer may review this one publication only.

    Without a matching row here, a user with the global 'reviewer' role
    has no actual reviewing permission on anything (see
    _is_eligible_reviewer in api/routes/publications.py).
    """

    __tablename__ = "reviewer_assignments"
    __table_args__ = (
        CheckConstraint(
            "(institution_id IS NOT NULL) != (publication_id IS NOT NULL)",
            name="ck_reviewer_assignment_exactly_one_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reviewer_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    institution_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("institutions.id"), nullable=True
    )
    publication_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("publications.id"), nullable=True
    )
    assigned_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewer_user_id])
