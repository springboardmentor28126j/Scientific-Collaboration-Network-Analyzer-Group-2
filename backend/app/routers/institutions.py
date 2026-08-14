from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
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

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="create_institution", details=f"Created institution: {new_institution.name}")
    db.add(log)
    db.commit()

    return new_institution


@router.get("/")
def list_institutions(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", regex="^(id|name|type|location)$"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    query = db.query(Institution)

    sort_column = getattr(Institution, sort_by)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    offset = (page - 1) * limit
    institutions = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "institutions": institutions
    }


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

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="update_institution", details=f"Updated institution: {inst.name}")
    db.add(log)
    db.commit()

    return inst


@router.delete("/{institution_id}")
def delete_institution(institution_id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    inst_name = inst.name

    db.delete(inst)
    db.commit()

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="delete_institution", details=f"Deleted institution: {inst_name}")
    db.add(log)
    db.commit()

    return {"message": "Institution deleted successfully"}