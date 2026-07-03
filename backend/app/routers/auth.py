from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserOut

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # TODO: hash password, save to DB, check duplicate email
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    # TODO: verify credentials, return JWT token
    raise HTTPException(status_code=501, detail="Not implemented yet")
