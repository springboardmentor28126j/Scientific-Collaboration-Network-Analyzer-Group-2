from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import SessionLocal
from app.oauth2 import get_current_user
from app.models import User, Institution

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


# ---------------- Create Institution ----------------

@router.post("/", response_model=schemas.InstitutionResponse)
def create_institution(
    institution: schemas.InstitutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can create institutions."
        )

    return crud.create_institution(db, institution)


# ---------------- View All Institutions ----------------

@router.get("/")
def get_all_institutions(
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "name",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in [
        "system_admin",
        "institution_admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    institutions, pagination = crud.get_all_institutions(
        db,
        page,
        page_size,
        sort_by,
        order
    )

    return {
        "data": institutions,
        "pagination": pagination
    }

# ---------------- Public Institutions (Registration Dropdown) ----------------

@router.get("/public")
def get_public_institutions(
    db: Session = Depends(get_db)
):

    institutions = db.query(Institution).all()

    return [
        {
            "id": institution.id,
            "name": institution.name
        }
        for institution in institutions
    ]
# ---------------- Institution Admin Profile ----------------

@router.post("/profile", response_model=schemas.InstitutionResponse)
def create_institution_profile(
    institution: schemas.InstitutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "institution_admin":
        raise HTTPException(
            status_code=403,
            detail="Only Institution Admin can update institution profile."
        )

    existing = db.query(Institution).filter(
        Institution.user_id == current_user.id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Institution not found."
        )

    existing.institution_type = institution.institution_type
    existing.location = institution.location
    existing.website = institution.website
    existing.phone = institution.phone

    db.commit()
    db.refresh(existing)

    return existing


# ---------------- My Institution ----------------

@router.get("/profile/me", response_model=schemas.InstitutionResponse)
def get_my_institution_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "institution_admin":
        raise HTTPException(
            status_code=403,
            detail="Only Institution Admin can access this profile."
        )

    institution = db.query(Institution).filter(
        Institution.user_id == current_user.id
    ).first()

    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution profile not found"
        )

    return institution


# ---------------- Update My Institution ----------------

@router.put("/profile", response_model=schemas.InstitutionResponse)
def update_my_institution_profile(
    institution: schemas.InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "institution_admin":
        raise HTTPException(
            status_code=403,
            detail="Only Institution Admin can update this profile."
        )

    existing = db.query(Institution).filter(
        Institution.user_id == current_user.id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Institution profile not found"
        )

    existing.institution_type = institution.institution_type
    existing.location = institution.location
    existing.website = institution.website
    existing.phone = institution.phone

    db.commit()
    db.refresh(existing)

    return existing


# ---------------- Get Institution ----------------

@router.get("/{institution_id}", response_model=schemas.InstitutionResponse)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    institution = crud.get_institution_by_id(db, institution_id)

    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    return institution


# ---------------- Update Institution ----------------

@router.put("/{institution_id}", response_model=schemas.InstitutionResponse)
def update_institution(
    institution_id: int,
    institution: schemas.InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can update institutions."
        )

    updated = crud.update_institution(
        db,
        institution_id,
        institution
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    return updated


# ---------------- Delete Institution ----------------

@router.delete("/{institution_id}")
def delete_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can delete institutions."
        )

    deleted = crud.delete_institution(
        db,
        institution_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    return {
        "message": "Institution deleted successfully"
    }


# ---------------- Institution Conferences ----------------

@router.get("/{institution_id}/conferences")
def get_institution_conferences(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    institution = crud.get_institution_by_id(
        db,
        institution_id
    )

    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    conferences = crud.get_conferences_by_institution(
        db,
        institution.name
    )

    return conferences