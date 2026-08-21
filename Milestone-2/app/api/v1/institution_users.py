import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_user_service
from app.core.dependencies import require_institution_admin
from app.db.session import get_session
from app.models.research import ResearcherProfile
from app.models.user import User, UserRole
from app.schemas.institution import InstitutionUserRead
from app.schemas.research import ResearcherProfileRead, ResearcherProfileUpdate
from app.schemas.user import UserCreateByInstitution, UserUpdateByInstitution
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


@router.get("/{user_id}", response_model=InstitutionUserRead)
async def get_institution_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_institution_user(current_user.institution_id, user_id)


@router.patch("/{user_id}", response_model=InstitutionUserRead)
async def update_institution_user(
    user_id: uuid.UUID,
    payload: UserUpdateByInstitution,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_institution_user(current_user.institution_id, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_institution_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_institution_user(current_user.institution_id, user_id)


@router.get("/{user_id}/researcher-profile", response_model=ResearcherProfileRead)
async def get_researcher_profile(
    user_id: uuid.UUID,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
):
    researcher = await user_service.get_institution_user(current_user.institution_id, user_id)
    if researcher.role != UserRole.RESEARCHER:
        raise HTTPException(status_code=422, detail="Academic profiles are available only for researchers")
    profile = await session.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == researcher.id))
    if profile is None:
        profile = ResearcherProfile(user_id=researcher.id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    return profile


@router.put("/{user_id}/researcher-profile", response_model=ResearcherProfileRead)
async def update_researcher_profile(
    user_id: uuid.UUID,
    payload: ResearcherProfileUpdate,
    current_user: User = Depends(require_institution_admin),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
):
    researcher = await user_service.get_institution_user(current_user.institution_id, user_id)
    if researcher.role != UserRole.RESEARCHER:
        raise HTTPException(status_code=422, detail="Academic profiles are available only for researchers")
    profile = await session.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == researcher.id))
    if profile is None:
        profile = ResearcherProfile(user_id=researcher.id)
        session.add(profile)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    await session.commit()
    await session.refresh(profile)
    return profile


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
