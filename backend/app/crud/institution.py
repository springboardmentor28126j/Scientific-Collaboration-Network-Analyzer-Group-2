from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate, InstitutionUpdate


def get_institution(db: Session, institution_id: int) -> Institution | None:
    return db.get(Institution, institution_id)


def get_institution_by_name(db: Session, name: str) -> Institution | None:
    return db.execute(select(Institution).where(Institution.name == name)).scalar_one_or_none()


def list_institutions(db: Session, skip: int = 0, limit: int = 100) -> list[Institution]:
    return list(db.execute(select(Institution).offset(skip).limit(limit)).scalars())


def create_institution(db: Session, institution_in: InstitutionCreate) -> Institution:
    institution = Institution(**institution_in.model_dump())
    db.add(institution)
    db.commit()
    db.refresh(institution)
    return institution


def update_institution(
    db: Session, institution: Institution, institution_in: InstitutionUpdate
) -> Institution:
    for field, value in institution_in.model_dump(exclude_unset=True).items():
        setattr(institution, field, value)
    db.commit()
    db.refresh(institution)
    return institution


def delete_institution(db: Session, institution: Institution) -> None:
    db.delete(institution)
    db.commit()
