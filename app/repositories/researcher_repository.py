from uuid import UUID

from sqlalchemy.orm import Session

from app.models.researcher import Researcher


class ResearcherRepository:

    @staticmethod
    def create(
        db: Session,
        researcher: Researcher,
    ):
        db.add(researcher)
        db.commit()
        db.refresh(researcher)
        return researcher

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(Researcher)
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        researcher_id: UUID,
    ):
        return (
            db.query(Researcher)
            .filter(
                Researcher.id == researcher_id
            )
            .first()
        )

    @staticmethod
    def get_by_user_id(
        db: Session,
        user_id: UUID,
    ):
        return (
            db.query(Researcher)
            .filter(
                Researcher.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        researcher: Researcher,
    ):
        db.commit()
        db.refresh(researcher)
        return researcher

    @staticmethod
    def delete(
        db: Session,
        researcher: Researcher,
    ):
        db.delete(researcher)
        db.commit()
