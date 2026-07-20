from sqlalchemy.orm import Session
from . import models, schemas


def create_researcher(
    db: Session,
    researcher: schemas.ResearcherCreate,
    user_id: int
):
    db_researcher = models.Researcher(
        user_id=user_id,
        full_name=researcher.full_name,
        email=researcher.email,
        department=researcher.department,
        institution=researcher.institution,
        designation=researcher.designation,
        research_interests=researcher.research_interests,
        skills=researcher.skills,
        phone=researcher.phone
    )

    db.add(db_researcher)
    db.commit()
    db.refresh(db_researcher)

    return db_researcher


def get_all_researchers(db: Session):
    return db.query(models.Researcher).all()


def get_researcher_by_id(db: Session, researcher_id: int):
    return db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()


def update_researcher(
    db: Session,
    researcher_id: int,
    researcher: schemas.ResearcherUpdate
):
    db_researcher = db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()

    if db_researcher:
        for key, value in researcher.model_dump().items():
            setattr(db_researcher, key, value)

        db.commit()
        db.refresh(db_researcher)

    return db_researcher


def delete_researcher(db: Session, researcher_id: int):
    db_researcher = db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()

    if db_researcher:
        db.delete(db_researcher)
        db.commit()

    return db_researcher
    
def create_publication(db: Session, publication: schemas.PublicationCreate):

    publication_data = publication.model_dump()

    db_publication = models.Publication(**publication_data)

    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)

    return db_publication


def get_all_publications(db: Session):
    return db.query(models.Publication).all()


def get_publication_by_id(db: Session, publication_id: int):
    return db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()


def update_publication(
    db: Session,
    publication_id: int,
    publication: schemas.PublicationUpdate
):
    db_publication = db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()

    if db_publication:
        for key, value in publication.model_dump().items():
            setattr(db_publication, key, value)

        db.commit()
        db.refresh(db_publication)

    return db_publication


def delete_publication(db: Session, publication_id: int):
    db_publication = db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()

    if db_publication:
        db.delete(db_publication)
        db.commit()

    return db_publication
def create_institution(db: Session, institution: schemas.InstitutionCreate):
    db_institution = models.Institution(**institution.model_dump())

    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)

    return db_institution


def get_all_institutions(db: Session):
    return db.query(models.Institution).all()


def get_institution_by_id(db: Session, institution_id: int):
    return db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()


def update_institution(
    db: Session,
    institution_id: int,
    institution: schemas.InstitutionUpdate
):
    db_institution = db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()

    if db_institution:
        for key, value in institution.model_dump().items():
            setattr(db_institution, key, value)

        db.commit()
        db.refresh(db_institution)

    return db_institution


def delete_institution(db: Session, institution_id: int):
    db_institution = db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()

    if db_institution:
        db.delete(db_institution)
        db.commit()

    return db_institution
def create_conference(db: Session, conference: schemas.ConferenceCreate):
    db_conference = models.Conference(**conference.model_dump())
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference


def get_all_conferences(db: Session):
    return db.query(models.Conference).all()


def get_conference_by_id(db: Session, conference_id: int):
    return db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()


def update_conference(
    db: Session,
    conference_id: int,
    conference: schemas.ConferenceUpdate
):
    db_conference = db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()

    if db_conference:
        for key, value in conference.model_dump().items():
            setattr(db_conference, key, value)

        db.commit()
        db.refresh(db_conference)

    return db_conference


def delete_conference(db: Session, conference_id: int):
    db_conference = db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()

    if db_conference:
        db.delete(db_conference)
        db.commit()

    return db_conference