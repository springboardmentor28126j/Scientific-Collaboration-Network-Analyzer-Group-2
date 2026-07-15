from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)

    if not db_user:
        return {"message": "User not found"}

    if not auth.verify_password(user.password, db_user.password):
        return {"message": "Invalid password"}

    return {
        "message": "Login Successful",
        "user": db_user.name
    }