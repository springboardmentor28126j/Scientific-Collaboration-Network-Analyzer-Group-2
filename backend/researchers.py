from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Researcher
from schemas import ResearcherCreate, ResearcherResponse

router = APIRouter()


# Create Researcher
@router.post("/researchers")
def create_researcher(
    researcher: ResearcherCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Researcher).filter(
        Researcher.email == researcher.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

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

    return {
        "message": "Researcher added successfully",
        "researcher": new_researcher
    }


# Get All Researchers
@router.get("/researchers", response_model=list[ResearcherResponse])
def get_researchers(db: Session = Depends(get_db)):
    return db.query(Researcher).all()


# Get Single Researcher
@router.get("/researchers/{researcher_id}", response_model=ResearcherResponse)
def get_researcher(
    researcher_id: int,
    db: Session = Depends(get_db)
):
    researcher = db.query(Researcher).filter(
        Researcher.researcher_id == researcher_id
    ).first()

    if researcher is None:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    return researcher


# Update Researcher
@router.put("/researchers/{researcher_id}")
def update_researcher(
    researcher_id: int,
    researcher: ResearcherCreate,
    db: Session = Depends(get_db)
):
    db_researcher = db.query(Researcher).filter(
        Researcher.researcher_id == researcher_id
    ).first()

    if db_researcher is None:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    db_researcher.full_name = researcher.full_name
    db_researcher.email = researcher.email
    db_researcher.institution = researcher.institution
    db_researcher.department = researcher.department
    db_researcher.country = researcher.country

    db.commit()
    db.refresh(db_researcher)

    return {
        "message": "Researcher updated successfully",
        "researcher": db_researcher
    }


# Delete Researcher
@router.delete("/researchers/{researcher_id}")
def delete_researcher(
    researcher_id: int,
    db: Session = Depends(get_db)
):
    researcher = db.query(Researcher).filter(
        Researcher.researcher_id == researcher_id
    ).first()

    if researcher is None:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    db.delete(researcher)
    db.commit()

    return {
        "message": "Researcher deleted successfully"
    }