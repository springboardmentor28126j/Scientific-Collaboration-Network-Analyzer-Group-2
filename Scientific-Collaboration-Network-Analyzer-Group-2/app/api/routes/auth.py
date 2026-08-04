from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import get_db, get_current_user

from app.schemas.auth import (
    LoginRequest,
    Token,
)

from app.schemas.user import (
    UserCreate,
    UserResponse,
)

from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.register(
            db,
            user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    token = AuthService.login(
        db,
        request.email,
        request.password,
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/token", response_model=Token)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    token = AuthService.login(
        db,
        form_data.username,
        form_data.password,
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.get("/me")
def me(
    current_user=Depends(get_current_user),
):
    return current_user
