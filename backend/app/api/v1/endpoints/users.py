from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole, AffiliationStatus
from app.repositories import user_repository
from app.schemas.user import UserOut, UserUpdate, UserAdminUpdate, InstitutionSelect
from app.core.security import hash_password
from app.services import user_service
from app.utils.audit import write_audit_log
from app.utils.notifications import notify

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


@router.post("/me/institution", response_model=UserOut)
def set_my_institution(
    payload: InstitutionSelect, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return user_service.set_researcher_institution(db, current_user, payload.institution_id)


@router.get("", response_model=list[UserOut])
def list_users(
    institution_id: int | None = None,
    role: UserRole | None = None,
    affiliation_status: AffiliationStatus | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    # Institution admins are scoped to their own institution regardless of query param.
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        institution_id = current_user.institution_id
    return user_repository.list_users(
        db, institution_id=institution_id, role=role, affiliation_status=affiliation_status,
        page=page, page_size=page_size,
    )


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


def _require_manageable_researcher(current_user: User, user: User) -> None:
    """
    Institution admins may only manage RESEARCHER accounts inside their own
    institution (BR: "Institution Admin: Researchers CRUD" / "Cannot manage
    system users"). System admins are unrestricted and never hit this check.
    """
    if current_user.role != UserRole.INSTITUTION_ADMIN:
        return
    if user.role != UserRole.RESEARCHER or user.institution_id != current_user.institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institution admins can only manage researcher accounts within their own institution",
        )


@router.patch("/{user_id}", response_model=UserOut)
def admin_update_user(
    user_id: int,
    payload: UserAdminUpdate,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    _require_manageable_researcher(current_user, user)

    if payload.role is not None:
        # Role changes are a system-wide privilege escalation concern -- only
        # System Admin can do this, even for an institution admin's own researchers.
        if current_user.role != UserRole.SYSTEM_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only a system admin can change a user's role")
        # System Admin accounts can only be created by inserting directly
        # into PostgreSQL -- there's no in-app path to this role, including
        # promotion by an existing System Admin.
        if payload.role == UserRole.SYSTEM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System Admin accounts cannot be granted through the app. They must be created directly in the database.",
            )
        user.role = payload.role
    was_active = user.is_active
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    write_audit_log(db, current_user.user_id, "UPDATE", "user", user.user_id, f"Admin update by {current_user.email}")
    if was_active and payload.is_active is False:
        notify(
            db, user.user_id, "account_deactivated", "Your account has been deactivated",
            "An administrator deactivated your account. Contact your institution admin or platform support if this is unexpected.",
        )
    return user


@router.delete("/{user_id}", status_code=204)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    _require_manageable_researcher(current_user, user)

    user.is_active = False  # Soft delete, per audit/compliance requirement (BR9)
    db.commit()
    write_audit_log(db, current_user.user_id, "DELETE", "user", user.user_id, "Soft delete (deactivation)")
    notify(
        db, user.user_id, "account_deactivated", "Your account has been deactivated",
        "An administrator deactivated your account. Contact your institution admin or platform support if this is unexpected.",
    )
    return None


@router.post("/{user_id}/approve-affiliation", response_model=UserOut)
def approve_affiliation(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    _require_manageable_researcher(current_user, user)
    if user.affiliation_status != AffiliationStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This account has no pending affiliation request")

    user.affiliation_status = AffiliationStatus.APPROVED
    if not user.is_active:
        # Institution Admin applications are created inactive and can't log
        # in until this approval -- BR: "System Admin Approval -> Institution
        # Admin Activated".
        user.is_active = True
    db.commit()
    db.refresh(user)
    write_audit_log(db, current_user.user_id, "UPDATE", "user", user.user_id, "Affiliation approved")
    notify(
        db, user.user_id, "affiliation_approved", "Institution affiliation approved",
        "Your institution affiliation request has been approved.",
        link_url="/profile",
    )
    return user


@router.post("/{user_id}/reject-affiliation", response_model=UserOut)
def reject_affiliation(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    _require_manageable_researcher(current_user, user)
    if user.affiliation_status != AffiliationStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This account has no pending affiliation request")

    user.affiliation_status = AffiliationStatus.REJECTED
    db.commit()
    db.refresh(user)
    write_audit_log(db, current_user.user_id, "UPDATE", "user", user.user_id, "Affiliation rejected")
    notify(
        db, user.user_id, "affiliation_rejected", "Institution affiliation rejected",
        "Your institution affiliation request was not approved. Contact your institution admin for details.",
        link_url="/profile",
    )
    return user
