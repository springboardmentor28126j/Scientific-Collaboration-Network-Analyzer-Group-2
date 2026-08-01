from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    DateTime
)

from sqlalchemy.sql import func

from app.database.database import Base


class ProjectTask(Base):

    __tablename__ = "project_tasks"

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

    milestone_id = Column(
        Integer,
        ForeignKey("project_milestones.id"),
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    deadline = Column(
        Date,
        nullable=False
    )

    priority = Column(
        String,
        default="Medium"
    )

    status = Column(
        String,
        default="Pending"
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