from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get("/publications-count")
def publications_count(db: Session = Depends(get_db)):
    return {"publications_count": crud.count_publications(db)}

@router.get("/collaborations-count")
def collaborations_count(db: Session = Depends(get_db)):
    return {"collaborations_count": crud.count_collaborations(db)}
