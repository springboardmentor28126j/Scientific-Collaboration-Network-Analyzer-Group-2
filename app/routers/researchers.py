from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud
from app.schemas.researcher import (
    ResearcherCreate,
    ResearcherResponse,
)

router = APIRouter(
    prefix="/researchers",
    tags=["Researchers"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ResearcherResponse])
def get_researchers(db: Session = Depends(get_db)):
    return crud.get_all_researchers(db)


@router.post("/", response_model=ResearcherResponse)
def add_researcher(
    researcher: ResearcherCreate,
    db: Session = Depends(get_db)
):
    return crud.create_researcher(db, researcher)