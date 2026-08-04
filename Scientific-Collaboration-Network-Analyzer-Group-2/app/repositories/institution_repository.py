from uuid import UUID

from sqlalchemy.orm import Session

from app.models.institution import Institution


class InstitutionRepository:

    @staticmethod
    def create(db: Session, institution: Institution):
        db.add(institution)
        db.commit()
        db.refresh(institution)
        return institution

    @staticmethod
    def get_all(db: Session):
        return db.query(Institution).all()

    @staticmethod
    def get_by_id(db: Session, institution_id: UUID):
        return (
            db.query(Institution)
            .filter(Institution.id == institution_id)
            .first()
        )

    @staticmethod
    def get_by_name(db: Session, name: str):
        return (
            db.query(Institution)
            .filter(Institution.name == name)
            .first()
        )

    @staticmethod
    def delete(db: Session, institution: Institution):
        db.delete(institution)
        db.commit()
