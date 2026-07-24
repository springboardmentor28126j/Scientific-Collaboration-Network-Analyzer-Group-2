from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.core.auth import oauth2_scheme, decode_access_token
from app import crud

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    email = payload.get("sub")

    return crud.get_user_by_email(
        db,
        email
    )


@router.get("/stats")
def dashboard_stats(

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return crud.get_dashboard_stats(

        db,

        current_user.id

    )