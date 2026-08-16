from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories import user_repository
from app.schemas.user import UserOut, UserUpdate, UserAdminUpdate
from app.core.security import hash_password
from app.utils.audit import write_audit_log

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_my_account(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_my_account(
    payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if payload.email:
        current_user.email = payload.email
    if payload.password:
        current_user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(current_user)
    write_audit_log(db, current_user.user_id, "UPDATE", "user", current_user.user_id, "Self-update")
    return current_user


@router.get("", response_model=list[UserOut])
def list_users(
    institution_id: int | None = None,
    role: UserRole | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    # Institution admins are scoped to their own institution regardless of query param.
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        institution_id = current_user.institution_id
    return user_repository.list_users(db, institution_id=institution_id, role=role, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.role == UserRole.INSTITUTION_ADMIN and user.institution_id != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access users outside your institution")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def admin_update_user(
    user_id: int,
    payload: UserAdminUpdate,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    write_audit_log(db, current_user.user_id, "UPDATE", "user", user.user_id, f"Admin update by {current_user.email}")
    return user


@router.delete("/{user_id}", status_code=204)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False  # Soft delete, per audit/compliance requirement (BR9)
    db.commit()
    write_audit_log(db, current_user.user_id, "DELETE", "user", user.user_id, "Soft delete (deactivation)")
    return None
