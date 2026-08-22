import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_user_service
from app.core.dependencies import require_institution_admin
from app.models.user import User, UserRole
from app.schemas.institution import InstitutionUserRead
from app.schemas.user import UserCreateByInstitution
from app.services.user_service import UserService

router = APIRouter(
    prefix="/institution/users",
    tags=["Institution Users"],
    dependencies=[Depends(require_institution_admin)],
)


@router.post(
    "",
    response_model=InstitutionUserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Researcher or Reviewer under your institution",
    description=(
        "Institution-admin only. Creates a Researcher or Reviewer scoped "
        "to the caller's own institution and emails them an invite-"
        "verification link. The account stays unverified/inactive until "
        "they follow that link and set a password."
    ),
)
async def create_institution_user(
    payload: UserCreateByInstitution,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_institution_user(
        institution_id=current_user.institution_id,
        institution_name=current_user.institution.name,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[InstitutionUserRead],
    summary="List Researchers/Reviewers under your institution",
)
async def list_institution_users(
    role: UserRole | None = Query(default=None, description="Filter by RESEARCHER or REVIEWER"),
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.list_institution_users(current_user.institution_id, role)


@router.patch(
    "/{user_id}/activate",
    response_model=InstitutionUserRead,
    summary="Activate a Researcher/Reviewer under your institution",
)
async def activate_institution_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.set_user_active(current_user.institution_id, user_id, True)


@router.patch(
    "/{user_id}/deactivate",
    response_model=InstitutionUserRead,
    summary="Deactivate a Researcher/Reviewer under your institution",
)
async def deactivate_institution_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.set_user_active(current_user.institution_id, user_id, False)
