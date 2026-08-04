from uuid import UUID
from sqlalchemy.orm import Session

from app.models.collaboration import Collaboration, CollaborationStatus


class CollaborationRepository:

    @staticmethod
    def create(db: Session, collaboration: Collaboration):
        db.add(collaboration)
        db.commit()
        db.refresh(collaboration)
        return collaboration

    @staticmethod
    def get_by_id(db: Session, collaboration_id: UUID):
        return (
            db.query(Collaboration)
            .filter(Collaboration.id == collaboration_id)
            .first()
        )

    @staticmethod
    def get_pending_requests(db: Session, receiver_id: UUID):
        return (
            db.query(Collaboration)
            .filter(
                Collaboration.receiver_id == receiver_id,
                Collaboration.status == CollaborationStatus.PENDING,
            )
            .all()
        )

    @staticmethod
    def get_all(db: Session):
        return db.query(Collaboration).all()

    @staticmethod
    def update(db: Session, collaboration: Collaboration):
        db.commit()
        db.refresh(collaboration)
        return collaboration

    @staticmethod
    def delete(db: Session, collaboration: Collaboration):
        db.delete(collaboration)
        db.commit()