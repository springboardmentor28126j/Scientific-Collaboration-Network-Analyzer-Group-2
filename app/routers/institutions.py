from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud

from app.schemas.institution import (
    InstitutionCreate,
    InstitutionResponse,
)

from app.models.institution import Institution

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
# ==========================================
# GET SINGLE INSTITUTION
# ==========================================

@router.get("/{institution_id}", response_model=InstitutionResponse)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db)
):

    institution = db.query(Institution).filter(
        Institution.id == institution_id
    ).first()

    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    return institution


# ==========================================
# UPDATE INSTITUTION
# ==========================================

@router.put("/{institution_id}", response_model=InstitutionResponse)
def update_institution(

    institution_id: int,

    institution: InstitutionCreate,

    db: Session = Depends(get_db)

):

    db_institution = db.query(Institution).filter(
        Institution.id == institution_id
    ).first()

    if not db_institution:

        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    db_institution.name = institution.name
    db_institution.country = institution.country
    db_institution.city = institution.city
    db_institution.website = institution.website

    db.commit()
    db.refresh(db_institution)

    return db_institution


# ==========================================
# DELETE INSTITUTION
# ==========================================

@router.delete("/{institution_id}")
def delete_institution(

    institution_id: int,

    db: Session = Depends(get_db)

):

    institution = db.query(Institution).filter(
        Institution.id == institution_id
    ).first()

    if not institution:

        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    db.delete(institution)
    db.commit()

    return {
        "message": "Institution deleted successfully"
    }