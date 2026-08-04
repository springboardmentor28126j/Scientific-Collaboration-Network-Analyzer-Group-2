import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base


class PublicationAuthor(Base):
    __tablename__ = "publication_authors"

    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "publications.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    researcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "researchers.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    author_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    is_corresponding_author: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
