from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check karo email pehle se exist to nahi karta
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Password ko hash karo (plain text save nahi karte, security ke liye)
    hashed_pw = hash_password(user.password)

    # Naya user banao aur database mein save karo
    new_user = User(
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    # User dhoondo email se
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Password verify karo
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # JWT token banao
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})

    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}