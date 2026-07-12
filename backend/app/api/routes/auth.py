from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud.institution import get_institution
from app.crud.user import authenticate_user, create_user, get_user_by_email
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])

SELF_REGISTERABLE_ROLES = {
    UserRole.RESEARCHER,
    UserRole.REVIEWER,
    UserRole.SYSTEM_ADMIN,
}


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_in.role not in SELF_REGISTERABLE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Self-registration is only permitted for the researcher or reviewer roles. "
                "Institution Admin and System Admin accounts must be created by an existing administrator."
            ),
        )

    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if user_in.institution_id is not None and get_institution(db, user_in.institution_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Institution not found")

    return create_user(db, user_in)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=access_token)
