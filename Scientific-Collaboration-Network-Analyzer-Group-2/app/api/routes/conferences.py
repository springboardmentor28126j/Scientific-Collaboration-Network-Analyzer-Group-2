from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
)

from app.schemas.conference import (
    ConferenceCreate,
    ConferenceUpdate,
    ConferenceResponse,
)

from app.services.conference_service import ConferenceService

router = APIRouter(
    prefix="/conferences",
    tags=["Conferences"],
)


@router.post(
    "/",
    response_model=ConferenceResponse,
    status_code=201,
)
def create_conference(
    conference: ConferenceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ConferenceService.create_conference(
        db,
        conference,
    )


@router.get(
    "/",
    response_model=list[ConferenceResponse],
)
def get_conferences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ConferenceService.get_all_conferences(db)


@router.get(
    "/{conference_id}",
    response_model=ConferenceResponse,
)
def get_conference(
    conference_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ConferenceService.get_conference(
        db,
        conference_id,
    )


@router.put(
    "/{conference_id}",
    response_model=ConferenceResponse,
)
def update_conference(
    conference_id: UUID,
    conference: ConferenceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ConferenceService.update_conference(
        db,
        conference_id,
        conference,
    )


@router.delete(
    "/{conference_id}",
)
def delete_conference(
    conference_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ConferenceService.delete_conference(
        db,
        conference_id,
    )