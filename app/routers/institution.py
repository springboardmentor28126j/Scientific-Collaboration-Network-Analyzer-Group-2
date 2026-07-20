from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import schemas, crud
from app.oauth2 import get_current_user
from app.models import User

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


@router.post("/", response_model=schemas.InstitutionResponse)
def create_institution(
    institution: schemas.InstitutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_institution(db, institution)


@router.get("/", response_model=list[schemas.InstitutionResponse])
def get_all_institutions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_all_institutions(db)


@router.get("/{institution_id}", response_model=schemas.InstitutionResponse)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    institution = crud.get_institution_by_id(db, institution_id)

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution


@router.put("/{institution_id}", response_model=schemas.InstitutionResponse)
def update_institution(
    institution_id: int,
    institution: schemas.InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = crud.update_institution(db, institution_id, institution)

    if not updated:
        raise HTTPException(status_code=404, detail="Institution not found")

    return updated


@router.delete("/{institution_id}")
def delete_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = crud.delete_institution(db, institution_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Institution not found")

    return {"message": "Institution deleted successfully"}