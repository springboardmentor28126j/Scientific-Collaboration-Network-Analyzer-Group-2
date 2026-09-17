from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Researcher
from schemas import ResearcherCreate, ResearcherResponse

router = APIRouter(
    prefix="/researchers",
    tags=["Researchers"]
)

# Database Connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create Researcher
@router.post("/", response_model=ResearcherResponse)
def create_researcher(researcher: ResearcherCreate, db: Session = Depends(get_db)):
    new_researcher = Researcher(
        full_name=researcher.full_name,
        email=researcher.email,
        institution=researcher.institution,
        department=researcher.department,
        country=researcher.country
    )

    db.add(new_researcher)
    db.commit()
    db.refresh(new_researcher)

    return new_researcher


# Get All Researchers
@router.get("/", response_model=list[ResearcherResponse])
def get_researchers(db: Session = Depends(get_db)):
    return db.query(Researcher).all()