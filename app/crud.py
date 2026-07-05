from sqlalchemy.orm import Session

from app.models.research_paper import ResearchPaper
from app.models.researcher import Researcher

from app.schemas.research_paper import ResearchPaperCreate
from app.schemas.researcher import ResearcherCreate
 
from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate


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