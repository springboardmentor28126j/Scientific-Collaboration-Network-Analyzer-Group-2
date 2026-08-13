from __future__ import annotations

import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.publication import Publication
    from app.models.user import User


class PublicationHistoryAction(StrEnum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"

    PDF_UPDATED = "PDF_UPDATED"

    AUTHOR_ADDED = "AUTHOR_ADDED"
    AUTHOR_REMOVED = "AUTHOR_REMOVED"

    SUBMITTED = "SUBMITTED"
    RESUBMITTED = "RESUBMITTED"

    REVIEWER_ASSIGNED = "REVIEWER_ASSIGNED"
    REVIEWER_UNASSIGNED = "REVIEWER_UNASSIGNED"

    REVIEW_SUBMITTED = "REVIEW_SUBMITTED"

    REVISION_REQUESTED = "REVISION_REQUESTED"

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

    CONFERENCE_CREATED = "CONFERENCE_CREATED"
    CONFERENCE_UPDATED = "CONFERENCE_UPDATED"


class PublicationHistory(Base, TimestampMixin):
    __tablename__ = "publication_histories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "publications.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    action: Mapped[PublicationHistoryAction] = mapped_column(
        Enum(
            PublicationHistoryAction,
            name="publication_history_action_enum",
        ),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    publication: Mapped["Publication"] = relationship(
        "Publication",
        back_populates="history",
    )

    user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[performed_by],
        back_populates="publication_history",
    )
