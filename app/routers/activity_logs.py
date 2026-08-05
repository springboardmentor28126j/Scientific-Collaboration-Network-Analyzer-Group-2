from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.get(
    "/",
    response_model=list[schemas.ActivityLogResponse]
)
def get_recent_activities(
    db: Session = Depends(get_db)
):

    return crud.get_recent_activities(db)