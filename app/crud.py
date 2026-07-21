from sqlalchemy.orm import Session

from app.models.research_paper import ResearchPaper
from app.models.researcher import Researcher

from app.schemas.research_paper import (
    ResearchPaperCreate,
    ResearchPaperUpdate
)
from app.schemas.researcher import ResearcherCreate
 
from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate

from app.models.collaboration import Collaboration
from app.schemas.collaboration import CollaborationCreate

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


# -----------------------------
# Research Papers CRUD
# -----------------------------

def get_all_papers(db: Session):
    return db.query(ResearchPaper).all()


def get_paper_by_id(db: Session, paper_id: int):
    return db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id
    ).first()


def create_paper(db: Session, paper: ResearchPaperCreate):
    new_paper = ResearchPaper(**paper.model_dump())
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)
    return new_paper


# -----------------------------
# Researchers CRUD
# -----------------------------

def get_all_researchers(db: Session):
    return db.query(Researcher).all()


def get_researcher_by_id(db: Session, researcher_id: int):
    return db.query(Researcher).filter(
        Researcher.id == researcher_id
    ).first()


def create_researcher(db: Session, researcher: ResearcherCreate):
    new_researcher = Researcher(**researcher.model_dump())
    db.add(new_researcher)
    db.commit()
    db.refresh(new_researcher)
    return new_researcher


# -----------------------------
# Institutions CRUD
# -----------------------------

def get_all_institutions(db: Session):
    return db.query(Institution).all()


def get_institution_by_id(db: Session, institution_id: int):
    return db.query(Institution).filter(
        Institution.id == institution_id
    ).first()


def create_institution(db: Session, institution: InstitutionCreate):
    new_institution = Institution(**institution.model_dump())
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    return new_institution


# -----------------------------
# Collaborations CRUD
# -----------------------------

def get_all_collaborations(db: Session):
    return db.query(Collaboration).all()


def get_collaboration_by_id(db: Session, collaboration_id: int):
    return db.query(Collaboration).filter(
        Collaboration.id == collaboration_id
    ).first()


def create_collaboration(db: Session, collaboration: CollaborationCreate):
    new_collaboration = Collaboration(**collaboration.model_dump())
    db.add(new_collaboration)
    db.commit()
    db.refresh(new_collaboration)
    return new_collaboration


# -----------------------------
# Search APIs
# -----------------------------

def search_papers_by_title(db: Session, title: str):
    return (
        db.query(ResearchPaper)
        .filter(ResearchPaper.title.ilike(f"%{title}%"))
        .all()
    )
def search_researchers_by_name(db: Session, name: str):
    return (
        db.query(Researcher)
        .filter(Researcher.full_name.ilike(f"%{name}%"))
        .all()
    )
def search_researchers_by_specialization(db: Session, specialization: str):
    return (
        db.query(Researcher)
        .filter(
            Researcher.specialization.ilike(f"%{specialization}%")
        )
        .all()
    )
def search_institutions_by_country(db: Session, country: str):
    return (
        db.query(Institution)
        .filter(Institution.country.ilike(f"%{country}%"))
        .all()
    )
# -----------------------------
# User Authentication CRUD
# -----------------------------

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):

    new_user = User(

        # Basic Details
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),

        # Personal Details
        phone_number=user.phone_number,
        gender=user.gender,
        date_of_birth=user.date_of_birth,

        # Academic Details
        institution=user.institution,
        department=user.department,
        designation=user.designation,

        # Research Details
        specialization=user.specialization,
        research_interests=user.research_interests,

        # Location
        # Location
        country=user.country,
        state=user.state,
        city=user.city,

        # Institution Details
        website=user.website,
        established_year=user.established_year,
        institution_type=user.institution_type,

        # Role
            role=user.role

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
# -----------------------------
# Update User Profile
# -----------------------------

from app.schemas.user import UserUpdate


def update_user(
    db: Session,
    db_user: User,
    user: UserUpdate
):

    update_data = user.model_dump(exclude_unset=True)

    for key, value in update_data.items():

        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user
# -----------------------------
# Get Papers by Researcher
# -----------------------------
def get_my_papers(
    db: Session,
    researcher_id: int
):
    return (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.researcher_id == researcher_id
        )
        .all()
    )


# -----------------------------
# Update Paper
# -----------------------------
def update_paper(
    db: Session,
    db_paper: ResearchPaper,
    updated_paper: ResearchPaperUpdate
):

    update_data = updated_paper.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            db_paper,
            key,
            value
        )

    db.commit()

    db.refresh(db_paper)

    return db_paper


# -----------------------------
# Delete Paper
# -----------------------------
def delete_paper(
    db: Session,
    db_paper: ResearchPaper
):

    db.delete(db_paper)

    db.commit()

    return {
        "message": "Paper deleted successfully"
    }