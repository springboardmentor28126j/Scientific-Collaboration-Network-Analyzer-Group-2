from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class AuditLog(Base):
    """Module 9: Audit & Compliance. An append-only record of who did what
    to which entity. Rows are never updated or deleted by the app -- only
    inserted by log_audit() (see app/core/audit.py) and read back via
    GET /audit (System Admin only).
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Nullable: a failed login attempt against an unknown email has no user_id yet.
    user_id: Mapped[Optional[int]] = mapped_column(
        "actor_user_id", Integer, ForeignKey("users.id"), nullable=True
    )
    # Short verb/phrase, e.g. "login", "login_failed", "register",
    # "publication_created", "publication_reviewed", "project_deleted".
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # What kind of thing the action was performed on, e.g. "user",
    # "publication", "project", "collaboration_request". Nullable for
    # actions with no single target entity (e.g. a failed login).
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # Free-text human-readable detail, e.g. "email=x@y.com" or
    # "status: submitted -> published". Kept as plain text (not JSON) to
    # match this project's existing preference for simple TEXT columns
    # (see Publication.review_comment) over a JSON/JSONB column type.
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    user: Mapped[Optional["User"]] = relationship("User")
