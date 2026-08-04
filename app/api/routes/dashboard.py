from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_statistics(
    db: Session = Depends(get_db),
):
    return DashboardService.get_statistics(db)

@router.get("/publications-per-year")
def publications_per_year(
    db: Session = Depends(get_db),
):
    return DashboardService.publications_per_year(db)


@router.get("/publication-types")
def publication_types(
    db: Session = Depends(get_db),
):
    return DashboardService.publication_types(db)
