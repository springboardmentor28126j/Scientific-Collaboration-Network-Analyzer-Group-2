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
    researcher.skills = updated.skills
    researcher.research_interest = updated.research_interest
    researcher.designation = updated.designation

    db.commit()
    db.refresh(researcher)

    return researcher