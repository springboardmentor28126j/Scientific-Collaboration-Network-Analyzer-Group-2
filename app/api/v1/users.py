import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_user_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import ResearcherRead
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/researchers",
    response_model=list[ResearcherRead],
    summary="List all researchers",
    description=(
        "Returns all active and verified researchers across every institution. "
        "Supports optional searching by name or email."
    ),
)
async def list_researchers(
    search: str | None = Query(
        default=None,
        description="Search by researcher name or email",
    ),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.list_researchers(search)
