import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.publication import Publication
    from app.models.publication_author import PublicationAuthor
    from app.models.review_assignment import ReviewAssignment
    from app.models.publication_history import PublicationHistory


class UserRole(StrEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    INSTITUTION_ADMIN = "INSTITUTION_ADMIN"
    RESEARCHER = "RESEARCHER"
    REVIEWER = "REVIEWER"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A single users table across all roles, discriminated by `role`.

    Login gate is uniformly: is_verified AND is_active (see
    app/services/auth_service.py). Verifying an account (via the
    email-verify or invite-verify link) sets both flags to True in the
    same step — see docs/architecture.md §5 for the reasoning.

    institution_id is nullable only for SUPER_ADMIN; every other role
    must belong to exactly one institution.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(30), nullable=False, default=UserRole.RESEARCHER)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    institution: Mapped["Institution | None"] = relationship("Institution", back_populates="users")
    publications: Mapped[list["Publication"]] = relationship(
        "Publication",
        foreign_keys="Publication.created_by",
        back_populates="creator",
    )
    editor_decisions: Mapped[list["Publication"]] = relationship(
        "Publication",
        foreign_keys="Publication.decided_by",
        back_populates="editor",
    )
    authored_publications: Mapped[list["PublicationAuthor"]] = relationship(
        "PublicationAuthor",
    )
    review_assignments: Mapped[list["ReviewAssignment"]] = relationship(
        "ReviewAssignment",
        foreign_keys="ReviewAssignment.reviewer_id",
        back_populates="reviewer",
    )
    publication_history: Mapped[list["PublicationHistory"]] = relationship(
        "PublicationHistory",
        foreign_keys="PublicationHistory.performed_by",
        back_populates="user",
    )
