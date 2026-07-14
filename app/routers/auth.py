from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import SessionLocal

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate
)

from app import crud

from app.core.security import verify_password
from app.core.auth import (
    create_access_token,
    decode_access_token,
    oauth2_scheme
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Register
# -----------------------------
@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = crud.get_user_by_email(
        db,
        user.email
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return crud.create_user(
        db,
        user
    )


# -----------------------------
# Login (Frontend)
# -----------------------------
@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = crud.get_user_by_email(
        db,
        user.email
    )

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        db_user.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    return {

        "access_token": token,
        "token_type": "bearer",
        "username": db_user.username,
        "full_name": db_user.full_name,
        "role": db_user.role

    }


# -----------------------------
# Login (Swagger OAuth2)
# -----------------------------
@router.post("/token")
def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = crud.get_user_by_email(
        db,
        form_data.username
    )

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        db_user.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    return {

        "access_token": token,
        "token_type": "bearer"

    }


# -----------------------------
# Current User
# -----------------------------
@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(
        token
    )

    email = payload.get("sub")

    user = crud.get_user_by_email(
        db,
        email
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# -----------------------------
# Update Profile
# -----------------------------
@router.put(
    "/update-profile",
    response_model=UserResponse
)
def update_profile(
    updated_user: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(
        token
    )

    email = payload.get("sub")

    db_user = crud.get_user_by_email(
        db,
        email
    )

    if not db_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return crud.update_user(
        db,
        db_user,
        updated_user
    )