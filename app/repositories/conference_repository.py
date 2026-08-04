from uuid import UUID
from sqlalchemy.orm import Session

from app.models.conference import Conference


class ConferenceRepository:

    @staticmethod
    def create(db: Session, conference: Conference):
        db.add(conference)
        db.commit()
        db.refresh(conference)
        return conference

    @staticmethod
    def get_all(db: Session):
        return db.query(Conference).all()

    @staticmethod
    def get_by_id(db: Session, conference_id: UUID):
        return (
            db.query(Conference)
            .filter(Conference.id == conference_id)
            .first()
        )

    @staticmethod
    def get_by_title(db: Session, title: str):
        return (
            db.query(Conference)
            .filter(Conference.title == title)
            .first()
        )

    @staticmethod
    def delete(db: Session, conference: Conference):
        db.delete(conference)
        db.commit()