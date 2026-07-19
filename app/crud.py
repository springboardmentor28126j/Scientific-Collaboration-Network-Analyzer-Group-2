from sqlalchemy.orm import Session
from app import models, schemas, auth

def create_user(db: Session, user: schemas.UserCreate):

    print("Password received:", user.password)
    print("Length:", len(user.password))

    hashed_password = auth.hash_password(user.password)

    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_researcher(db: Session, researcher: schemas.ResearcherCreate):
    db_researcher = models.Researcher(
        full_name=researcher.full_name,
        department=researcher.department,
        institution=researcher.institution,
        institution_id=researcher.institution_id,
        skills=researcher.skills,
        research_interest=researcher.research_interest,
        designation=researcher.designation
    )

    db.add(db_researcher)
    db.commit()
    db.refresh(db_researcher)

    return db_researcher

def get_researchers(db: Session):
    return db.query(models.Researcher).all()

def get_researcher_by_id(db: Session, id: int):
    return db.query(models.Researcher).filter(models.Researcher.id == id).first()

def update_researcher(db: Session, id: int, updated):
    researcher = db.query(models.Researcher).filter(models.Researcher.id == id).first()

    if not researcher:
        return None

    researcher.full_name = updated.full_name
    researcher.department = updated.department
    researcher.institution = updated.institution
    researcher.institution_id = updated.institution_id
    researcher.skills = updated.skills
    researcher.research_interest = updated.research_interest
    researcher.designation = updated.designation

    db.commit()
    db.refresh(researcher)

    return researcher

def create_institution(db: Session, institution: schemas.InstitutionCreate):
    db_institution = models.Institution(
        name=institution.name,
        address=institution.address,
        website=institution.website,
        contact_email=institution.contact_email
    )

    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)

    return db_institution


def get_institutions(db: Session):
    return db.query(models.Institution).all()


def get_institution_by_id(db: Session, institution_id: int):
    return (
        db.query(models.Institution)
        .filter(models.Institution.id == institution_id)
        .first()
    )


def update_institution(
    db: Session,
    institution_id: int,
    updated_institution: schemas.InstitutionCreate
):
    institution = get_institution_by_id(db, institution_id)

    if not institution:
        return None

    institution.name = updated_institution.name
    institution.address = updated_institution.address
    institution.website = updated_institution.website
    institution.contact_email = updated_institution.contact_email

    db.commit()
    db.refresh(institution)

    return institution


def delete_institution(db: Session, institution_id: int):
    institution = get_institution_by_id(db, institution_id)

    if not institution:
        return None

    db.delete(institution)
    db.commit()

    return institution

def create_publication(db: Session, publication: schemas.PublicationCreate):
    db_publication = models.Publication(
        title=publication.title,
        abstract=publication.abstract,
        publication_type=publication.publication_type,
        status=publication.status,
        doi=publication.doi,
        publication_date=publication.publication_date,
        journal_or_venue=publication.journal_or_venue,
        institution_id=publication.institution_id
    )

    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)

    return db_publication


def get_publications(db: Session):
    return db.query(models.Publication).all()

def get_publication_by_id(db: Session, publication_id: int):
    return (
        db.query(models.Publication)
        .filter(models.Publication.id == publication_id)
        .first()
    )

def update_publication(
    db: Session,
    publication_id: int,
    updated_publication: schemas.PublicationCreate
):
    publication = get_publication_by_id(db, publication_id)

    if not publication:
        return None

    publication.title = updated_publication.title
    publication.abstract = updated_publication.abstract
    publication.publication_type = updated_publication.publication_type
    publication.status = updated_publication.status
    publication.doi = updated_publication.doi
    publication.publication_date = updated_publication.publication_date
    publication.journal_or_venue = updated_publication.journal_or_venue
    publication.institution_id = updated_publication.institution_id

    db.commit()
    db.refresh(publication)

    return publication

def delete_publication(db: Session, publication_id: int):
    publication = get_publication_by_id(db, publication_id)

    if not publication:
        return None

    db.delete(publication)
    db.commit()

    return publication