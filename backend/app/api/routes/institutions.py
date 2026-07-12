from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.crud.institution import (
    create_institution,
    delete_institution,
    get_institution,
    get_institution_by_name,
    list_institutions,
    update_institution,
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.institution import InstitutionCreate, InstitutionRead, InstitutionUpdate

router = APIRouter(prefix="/institutions", tags=["Institution Management"])


@router.post("/", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED)
def create_new_institution(
    institution_in: InstitutionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    if get_institution_by_name(db, institution_in.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Institution already exists")
    return create_institution(db, institution_in)


@router.get("/", response_model=list[InstitutionRead])
def read_institutions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list_institutions(db, skip, limit)


@router.get("/{institution_id}", response_model=InstitutionRead)
def read_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    institution = get_institution(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return institution


def _ensure_institution_access(current_user: User, institution_id: int) -> None:
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return
    if current_user.role == UserRole.INSTITUTION_ADMIN and current_user.institution_id == institution_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to manage this institution",
    )


@router.put("/{institution_id}", response_model=InstitutionRead)
def update_existing_institution(
    institution_id: int,
    institution_in: InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)
    ),
):
    institution = get_institution(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    _ensure_institution_access(current_user, institution_id)
    return update_institution(db, institution, institution_in)


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    institution = get_institution(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    delete_institution(db, institution)
