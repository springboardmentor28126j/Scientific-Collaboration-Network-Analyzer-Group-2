import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_publication_conference_service
from app.core.dependencies import get_current_user

from app.models.user import User
from app.schemas.publication_conference import (
    PublicationConferenceCreate,
    PublicationConferenceRead,
    PublicationConferenceUpdate,
)
from app.services.publication_conference_service import PublicationConferenceService


router = APIRouter(
    prefix="/publications",
    tags=["Publications"],
)


@router.post(
    "/publications/{publication_id}/conference",
    response_model=PublicationConferenceRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_conference(
    publication_id: uuid.UUID,
    payload: PublicationConferenceCreate,
    current_user: User = Depends(get_current_user),
    service: PublicationConferenceService = Depends(
        get_publication_conference_service
    ),
):
    return await service.create_conference(
        publication_id=publication_id,
        payload=payload,
        current_user=current_user,
    )

@router.get(
    "/publications/{publication_id}/conference",
    response_model=PublicationConferenceRead,
)
async def get_conference(
    publication_id: uuid.UUID,
    service: PublicationConferenceService = Depends(
        get_publication_conference_service
    ),
):
    return await service.get_conference(publication_id)

@router.patch(
    "/publications/{publication_id}/conference",
    response_model=PublicationConferenceRead,
)
async def update_conference(
    publication_id: uuid.UUID,
    payload: PublicationConferenceUpdate,
    current_user: User = Depends(get_current_user),
    service: PublicationConferenceService = Depends(
        get_publication_conference_service
    ),
):
    return await service.update_conference(
        publication_id=publication_id,
        payload=payload,
        current_user=current_user,
    )

