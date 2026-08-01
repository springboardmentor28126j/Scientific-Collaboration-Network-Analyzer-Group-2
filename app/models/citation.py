from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func

from app.database.database import Base


class Citation(Base):

    __tablename__ = "citations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    paper_id = Column(
        Integer,
        ForeignKey("research_papers.id"),
        nullable=False
    )

    cited_paper_id = Column(
        Integer,
        ForeignKey("research_papers.id"),
        nullable=False
    )

    citation_year = Column(
        Integer,
        nullable=False
    )

    citation_count = Column(
        Integer,
        default=1
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )