from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate, InstitutionOut

router = APIRouter()


@router.post("/", response_model=InstitutionOut)
def create_institution(institution: InstitutionCreate, db: Session = Depends(get_db)):
    new_institution = Institution(**institution.dict())
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    return new_institution


@router.get("/", response_model=List[InstitutionOut])
def list_institutions(db: Session = Depends(get_db)):
    return db.query(Institution).all()


@router.get("/{institution_id}", response_model=InstitutionOut)
def get_institution(institution_id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    return inst


@router.put("/{institution_id}", response_model=InstitutionOut)
def update_institution(institution_id: int, institution_update: InstitutionCreate, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    for field, value in institution_update.dict().items():
        setattr(inst, field, value)

    db.commit()
    db.refresh(inst)
    return inst


@router.delete("/{institution_id}")
def delete_institution(institution_id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    db.delete(inst)
    db.commit()
    return {"message": "Institution deleted successfully"}