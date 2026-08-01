from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class InstitutionCollaborationRequest(Base):

    __tablename__ = "institution_collaboration_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sender_institution_id = Column(
        Integer,
        ForeignKey("institutions.id"),
        nullable=False
    )

    receiver_institution_id = Column(
        Integer,
        ForeignKey("institutions.id"),
        nullable=False
    )

    project_title = Column(
        String(200),
        nullable=False
    )

    purpose = Column(
        String(500),
        nullable=False
    )

    status = Column(
        String(30),
        default="Pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )