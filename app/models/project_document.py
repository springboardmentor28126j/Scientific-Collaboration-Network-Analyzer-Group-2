from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class ProjectDocument(Base):

    __tablename__ = "project_documents"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_type = Column(
        String(50)
    )

    file_url = Column(
        String(500)
    )

    description = Column(
        String(500)
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )