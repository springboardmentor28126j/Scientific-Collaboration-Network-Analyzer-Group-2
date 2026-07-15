from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/researchers",
    tags=["Researchers"]
)

@router.post("/")
def create_researcher(
    researcher: schemas.ResearcherCreate,
    db: Session = Depends(get_db)
):
    return crud.create_researcher(db=db, researcher=researcher)

@router.get("/")
def get_researchers(db: Session = Depends(get_db)):
    return crud.get_researchers(db=db)

@router.get("/{id}")
def get_researcher(id: int, db: Session = Depends(get_db)):
    return crud.get_researcher_by_id(db=db, id=id)

@router.put("/{id}")
def update_researcher(
    id: int,
    updated: schemas.ResearcherCreate,
    db: Session = Depends(get_db)
):
    return crud.update_researcher(db=db, id=id, updated=updated)