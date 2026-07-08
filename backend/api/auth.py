from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.connection import get_db
from dependencies.auth import get_current_user
from models.researcher import Researcher
from models.user import User
from schemas.user import (
    Token,
    UserRegister,
    UserResponse,
)
from utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    researcher = Researcher(
        user_id=new_user.id,
        full_name=user.full_name,
        institution=user.institution,
        department=user.department,
        designation=user.designation,
        research_interest=user.research_interest,
        skills=user.skills,
        bio=user.bio
    )

    db.add(researcher)
    db.commit()

    return new_user


@router.post(
    "/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    researcher = db.query(Researcher).filter(
        Researcher.user_id == current_user.id
    ).first()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "researcher": {
            "full_name": researcher.full_name,
            "institution": researcher.institution,
            "department": researcher.department,
            "designation": researcher.designation,
            "research_interest": researcher.research_interest,
            "skills": researcher.skills,
            "bio": researcher.bio
        }
    }