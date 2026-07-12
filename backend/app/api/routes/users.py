from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.crud.institution import get_institution
from app.crud.user import (
    create_user,
    get_user,
    get_user_by_email,
    list_users,
    update_user,
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserDetailRead, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if (
        user_in.institution_id is not None
        and get_institution(db, user_in.institution_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution not found",
        )

    return create_user(db, user_in)


@router.get("/me", response_model=UserDetailRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserDetailRead)
def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_user(db, current_user, user_in)


@router.get("/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    return list_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserDetailRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)
    ),
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user