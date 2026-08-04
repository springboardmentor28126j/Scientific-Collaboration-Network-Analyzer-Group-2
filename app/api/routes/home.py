from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.home_service import HomeService

router = APIRouter(
    prefix="/home",
    tags=["Home"],
)


@router.get("")
def home(db: Session = Depends(get_db)):
    return HomeService.get_home_data(db)
