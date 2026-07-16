import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.publication import Publication
    from app.models.user import User


class PublicationAuthor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Links researchers to publications.

    One publication can have many authors.

    One researcher can contribute to many publications.
    """

    __tablename__ = "publication_authors"

    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publications.id", ondelete="CASCADE"),
        nullable=False,
    )

    researcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    author_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_corresponding_author: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    publication: Mapped["Publication"] = relationship(
        "Publication",
        back_populates="authors",
    )

    researcher: Mapped["User"] = relationship("User")
