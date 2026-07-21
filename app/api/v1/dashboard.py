from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.api.deps import get_dashboard_service

from app.models.user import User
from app.schemas.dashboard import ReviewerDashboard, SuperAdminDashboard, InstitutionDashboard, ResearcherDashboard
from app.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "",
    response_model=(
        SuperAdminDashboard
        | InstitutionDashboard
        | ResearcherDashboard
        | ReviewerDashboard
    ),
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.get_dashboard(current_user)
