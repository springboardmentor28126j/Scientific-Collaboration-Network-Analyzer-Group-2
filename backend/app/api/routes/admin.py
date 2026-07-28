from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
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
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user