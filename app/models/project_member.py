from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func

from app.database.database import Base


class ProjectMember(Base):

    __tablename__ = "project_members"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    researcher_id = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    role = Column(
        String(50),
        default="Co-Researcher"
    )

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )