from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class CollaborationRequest(Base):

    __tablename__ = "collaboration_requests"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    receiver_id = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    # Selected paper for collaboration
    paper_id = Column(
        Integer,
        ForeignKey("research_papers.id"),
        nullable=False
    )

    message = Column(
        String(500)
    )

    status = Column(
        String(30),
        default="Pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )