from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionResponse,
)

router = APIRouter(
    prefix="/institutions",
    tags=["Institutions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[InstitutionResponse])
def get_institutions(db: Session = Depends(get_db)):
    return crud.get_all_institutions(db)

@router.get("/search", response_model=list[InstitutionResponse])
def search_institutions(
    country: str,
    db: Session = Depends(get_db)
):
    return crud.search_institutions_by_country(db, country)


@router.post("/", response_model=InstitutionResponse)
def add_institution(
    institution: InstitutionCreate,
    db: Session = Depends(get_db)
):
    return crud.create_institution(db, institution)