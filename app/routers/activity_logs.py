from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas
from ..oauth2 import get_current_user
from ..models import User


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.get(
    "/",
    response_model=list[schemas.ActivityLogResponse]
)
def get_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return crud.get_recent_activities(
        db=db,
        current_user=current_user,
        limit=20
    )