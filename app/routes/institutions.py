from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/institutions",
    tags=["Institutions"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_institution(
    institution: schemas.InstitutionCreate,
    db: Session = Depends(get_db)
):
    existing_institution = (
        db.query(crud.models.Institution)
        .filter(crud.models.Institution.name == institution.name)
        .first()
    )

    if existing_institution:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution with this name already exists"
        )

    return crud.create_institution(db, institution)


@router.get("/")
def get_institutions(db: Session = Depends(get_db)):
    return crud.get_institutions(db)


@router.get("/{institution_id}")
def get_institution(institution_id: int, db: Session = Depends(get_db)):
    institution = crud.get_institution_by_id(db, institution_id)

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )

    return institution


@router.put("/{institution_id}")
def update_institution(
    institution_id: int,
    updated_institution: schemas.InstitutionCreate,
    db: Session = Depends(get_db)
):
    institution = crud.update_institution(
        db,
        institution_id,
        updated_institution
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )

    return institution


@router.delete("/{institution_id}")
def delete_institution(institution_id: int, db: Session = Depends(get_db)):
    institution = crud.delete_institution(db, institution_id)

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )

    return {
        "message": "Institution deleted successfully",
        "institution_id": institution_id
    }

@router.get("/{institution_id}/report")
def institution_report(institution_id: int, db: Session = Depends(get_db)):
    return crud.get_institution_report(db, institution_id)
