from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
    require_admin,
)

from app.schemas.user import UserUpdate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# Get all users (Admin only)
@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return UserService.get_all_users(db)


# Get one user
@router.get("/{user_id}")
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return UserService.get_user(db, user_id)


# Update user
@router.put("/{user_id}")
def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = UserService.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if (
        current_user.id != user.id
        and current_user.role.name != "ADMIN"
    ):
        raise HTTPException(
            status_code=403,
            detail="Permission denied",
        )

    return UserService.update_user(
        db,
        user,
        data,
    )


# Delete user (Admin only)
@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    user = UserService.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    UserService.delete_user(
        db,
        user,
    )

    return {
        "message": "User deleted successfully"
    }
