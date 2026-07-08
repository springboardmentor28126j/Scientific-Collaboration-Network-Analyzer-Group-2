from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.researcher import Researcher
from schemas.user import UserRegister, UserResponse
from utils.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):

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