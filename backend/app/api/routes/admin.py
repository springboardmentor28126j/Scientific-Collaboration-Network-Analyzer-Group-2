from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.api.routes.notifications import create_notification
from app.core.audit import log_audit
from app.core.config import settings
from app.core.email import render_email, send_email
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.admin import AdminUserUpdate
from app.schemas.user import UserOut

router = APIRouter()


@router.get("/users", response_model=list[UserOut])
def list_users(
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> list[User]:
    return db.query(User).order_by(User.id).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id and payload.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't deactivate your own account",
        )
    if (
        user.id == current_user.id
        and payload.role is not None
        and payload.role != UserRole.SYSTEM_ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't demote your own account away from System Admin",
        )

    update_data = payload.model_dump(exclude_unset=True)

    was_pending_institution_admin = (
        user.role == UserRole.INSTITUTION_ADMIN
        and "is_active" in update_data
        and update_data["is_active"] is True
        and not user.is_active
    )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    if was_pending_institution_admin:
        create_notification(
            db,
            recipient_user_id=user.id,
            type="institution_admin_approved",
            message="Your Institution Admin application has been approved. You can now log in.",
            link="/login",
        )
        send_email(
            to_email=user.email,
            subject="Your Institution Admin application was approved",
            html_body=render_email(
                title="Application approved",
                body_html="<p>Your Institution Admin application has been approved. You can log in now.</p>",
                cta_text="Log In",
                cta_link=f"{settings.FRONTEND_URL}/login",
            ),
        )

    log_audit(
        db,
        actor_user_id=current_user.id,
        action="user_role_updated",
        entity_type="user",
        entity_id=user.id,
        details=str(update_data),
    )

    return user