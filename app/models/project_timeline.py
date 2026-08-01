from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class ProjectTimeline(Base):

    __tablename__ = "project_timelines"

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

    event_title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        String(500)
    )

    event_date = Column(
        Date,
        nullable=False
    )

    event_type = Column(
        String(50),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )