from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Citation(Base):
    __tablename__ = "citations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey("publications.id", ondelete="CASCADE"),
        nullable=False,
    )

    citing_title = Column(
        String,
        nullable=False,
    )

    citing_authors = Column(
        String,
        nullable=False,
    )

    journal = Column(
        String,
        nullable=True,
    )

    year = Column(
        Integer,
        nullable=True,
    )

    doi = Column(
        String,
        nullable=True,
        unique=True,
    )

    url = Column(
        String,
        nullable=True,
    )

    citation_type = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    publication = relationship(
        "Publication",
        back_populates="citations",
    )
