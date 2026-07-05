from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud
from app.schemas.collaboration import (
    CollaborationCreate,
    CollaborationResponse,
)

router = APIRouter(
    prefix="/collaborations",
    tags=["Collaborations"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[CollaborationResponse])
def get_collaborations(db: Session = Depends(get_db)):
    return crud.get_all_collaborations(db)


@router.post("/", response_model=CollaborationResponse)
def add_collaboration(
    collaboration: CollaborationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_collaboration(db, collaboration)