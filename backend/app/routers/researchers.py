from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.researcher import Researcher
from app.schemas.researcher import ResearcherCreate, ResearcherOut

router = APIRouter()


@router.post("/", response_model=ResearcherOut)
def create_researcher(researcher: ResearcherCreate, db: Session = Depends(get_db)):
    new_researcher = Researcher(**researcher.dict())
    db.add(new_researcher)
    db.commit()
    db.refresh(new_researcher)
    return new_researcher


@router.get("/", response_model=List[ResearcherOut])
def list_researchers(db: Session = Depends(get_db)):
    return db.query(Researcher).all()


@router.get("/{researcher_id}", response_model=ResearcherOut)
def get_researcher(researcher_id: int, db: Session = Depends(get_db)):
    researcher = db.query(Researcher).filter(Researcher.id == researcher_id).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")
    return researcher


@router.put("/{researcher_id}", response_model=ResearcherOut)
def update_researcher(researcher_id: int, researcher_update: ResearcherCreate, db: Session = Depends(get_db)):
    researcher = db.query(Researcher).filter(Researcher.id == researcher_id).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")

    for field, value in researcher_update.dict().items():
        setattr(researcher, field, value)

    db.commit()
    db.refresh(researcher)
    return researcher


@router.delete("/{researcher_id}")
def delete_researcher(researcher_id: int, db: Session = Depends(get_db)):
    researcher = db.query(Researcher).filter(Researcher.id == researcher_id).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")

    db.delete(researcher)
    db.commit()
    return {"message": "Researcher deleted successfully"}