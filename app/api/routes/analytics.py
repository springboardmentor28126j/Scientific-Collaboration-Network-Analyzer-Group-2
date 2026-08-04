from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.analytics import HomeAnalyticsResponse
from app.services.analytics_service import analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/home",
    response_model=HomeAnalyticsResponse,
)
def get_home_analytics(
    db: Session = Depends(get_db),
):
    return analytics_service.get_home_analytics(db)
