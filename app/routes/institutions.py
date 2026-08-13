from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas, auth
from app.database import get_db
from app.permissions import current_user, is_system_admin, require_system_admin

router = APIRouter(
    prefix="/institutions",
    tags=["Institutions"],
    dependencies=[Depends(auth.require_authenticated)]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_institution(
    institution: schemas.InstitutionCreate,
    _admin = Depends(require_system_admin),
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
def get_institutions(user = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(crud.models.Institution)
    if not is_system_admin(user) and user.role.lower() == "institution admin":
        query = query.filter(crud.models.Institution.id == user.institution_id) if user.institution_id else query.filter(False)
    return query.order_by(crud.models.Institution.name).all()


@router.get("/{institution_id}")
def get_institution(institution_id: int, user = Depends(current_user), db: Session = Depends(get_db)):
    institution = get_institutions(user, db)
    institution = next((item for item in institution if item.id == institution_id), None)

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
    _admin = Depends(require_system_admin),
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
def delete_institution(institution_id: int, _admin = Depends(require_system_admin), db: Session = Depends(get_db)):
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
    report = crud.get_institution_report(db, institution_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return report
