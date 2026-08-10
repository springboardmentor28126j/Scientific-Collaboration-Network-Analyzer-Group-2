from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.institution import Institution
from app.models.user import User, UserRole
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionOut,
)
from app.schemas.researcher import ResearcherOut

router = APIRouter()


def _get_institution(
    db: Session,
    institution_id: int,
) -> Institution:

    institution = (
        db.query(Institution)
        .filter(Institution.id == institution_id)
        .first()
    )

    if institution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found",
        )

    return institution


def _require_institution_admin_or_system_admin(
    current_user: User, institution: Institution
) -> None:
    """Only a System Admin, or the Institution Admin assigned to this
    specific institution, may modify it."""
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return
    if institution.admin_user_id == current_user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only a System Admin or this institution's admin can do that",
    )


def _validate_duplicate(
    db: Session,
    email: str,
    name: str,
):

    email_exists = (
        db.query(Institution)
        .filter(Institution.email == email)
        .first()
    )

    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution email already exists",
        )

    name_exists = (
        db.query(Institution)
        .filter(Institution.name == name)
        .first()
    )

    if name_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution already exists",
        )


@router.post(
    "/",
    response_model=InstitutionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_institution(
    payload: InstitutionCreate,
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):

    _validate_duplicate(
        db,
        payload.email,
        payload.name,
    )

    institution = Institution(**payload.model_dump())

    try:
        db.add(institution)
        db.commit()
        db.refresh(institution)
        return institution

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating institution",
        )


@router.get(
    "/",
    response_model=list[InstitutionOut],
)
def get_all_institutions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    institutions = (
        db.query(Institution)
        .all()
    )

    return institutions


@router.get(
    "/mine",
    response_model=list[InstitutionOut],
)
def get_my_institutions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Institutions the current user can create/manage conferences for:
    a System Admin sees every institution, an Institution Admin sees only
    the institution(s) they're assigned to, everyone else sees none."""
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return db.query(Institution).all()

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        return (
            db.query(Institution)
            .filter(Institution.admin_user_id == current_user.id)
            .all()
        )

    return []


@router.get(
    "/search/",
    response_model=list[InstitutionOut],
)
def search_institutions(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    institutions = (
        db.query(Institution)
        .filter(Institution.name.ilike(f"%{name}%"))
        .all()
    )

    return institutions


@router.get(
    "/{institution_id}",
    response_model=InstitutionOut,
)
def get_institution(
    institution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    institution = _get_institution(
        db,
        institution_id,
    )

    return institution


@router.put(
    "/{institution_id}",
    response_model=InstitutionOut,
)
def update_institution(
    institution_id: int,
    payload: InstitutionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    institution = _get_institution(
        db,
        institution_id,
    )

    _require_institution_admin_or_system_admin(current_user, institution)

    # Only a System Admin may reassign which user administers an institution.
    update_data = payload.model_dump(exclude_unset=True)
    if "admin_user_id" in update_data and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a System Admin can reassign an institution's admin",
        )

    if "email" in update_data:

        existing = (
            db.query(Institution)
            .filter(
                Institution.email == update_data["email"],
                Institution.id != institution_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Institution email already exists",
            )

    if "name" in update_data:

        existing = (
            db.query(Institution)
            .filter(
                Institution.name == update_data["name"],
                Institution.id != institution_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Institution already exists",
            )

    for field, value in update_data.items():
        setattr(institution, field, value)

    try:

        db.commit()

        db.refresh(institution)

        return institution

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating institution",
        )


@router.delete(
    "/{institution_id}",
    status_code=status.HTTP_200_OK,
)
def delete_institution(
    institution_id: int,
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):

    institution = _get_institution(
        db,
        institution_id,
    )

    try:

        db.delete(institution)

        db.commit()

        return {
            "message": "Institution deleted successfully"
        }

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting institution",
        )


@router.get(
    "/{institution_id}/researchers",
    response_model=list[ResearcherOut],
)
def get_institution_researchers(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    institution = _get_institution(
        db,
        institution_id,
    )

    return institution.researchers
