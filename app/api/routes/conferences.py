from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
)

from app.models.user import User

from app.schemas.conference import (
    ConferenceCreate,
    ConferenceUpdate,
    ConferenceResponse,
)

from app.schemas.conference_registration import (
    ConferenceRegistrationResponse,
)

from app.services.conference_service import ConferenceService
from app.services.conference_registration_service import (
    ConferenceRegistrationService,
)

router = APIRouter(
    prefix="/conferences",
    tags=["Conferences"],
)


# ==========================================
# Conference CRUD
# ==========================================

@router.post(
    "/",
    response_model=ConferenceResponse,
    status_code=201,
)
def create_conference(
    conference: ConferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConferenceService.create_conference(
        db=db,
        data=conference,
        current_user=current_user,
    )


@router.get(
    "/",
    response_model=list[ConferenceResponse],
)
def get_conferences(
    db: Session = Depends(get_db),
):
    return ConferenceService.get_all_conferences(db)


@router.get(
    "/{conference_id}",
    response_model=ConferenceResponse,
)
def get_conference(
    conference_id: UUID,
    db: Session = Depends(get_db),
):
    return ConferenceService.get_conference(
        db=db,
        conference_id=conference_id,
    )


@router.put(
    "/{conference_id}",
    response_model=ConferenceResponse,
)
def update_conference(
    conference_id: UUID,
    conference: ConferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConferenceService.update_conference(
        db=db,
        conference_id=conference_id,
        data=conference,
        current_user=current_user,
    )


@router.delete(
    "/{conference_id}",
)
def delete_conference(
    conference_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConferenceService.delete_conference(
        db=db,
        conference_id=conference_id,
        current_user=current_user,
    )


# ==========================================
# Conference Registration
# ==========================================

@router.post(
    "/{conference_id}/join",
    response_model=ConferenceRegistrationResponse,
)
def join_conference(
    conference_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConferenceRegistrationService.join_conference(
        db=db,
        conference_id=conference_id,
        current_user=current_user,
    )


@router.delete(
    "/{conference_id}/leave",
)
def leave_conference(
    conference_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConferenceRegistrationService.leave_conference(
        db=db,
        conference_id=conference_id,
        current_user=current_user,
    )


@router.get(
    "/joined",
    response_model=list[ConferenceResponse],
)
def get_joined_conferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConferenceRegistrationService.get_joined_conferences(
        db=db,
        current_user=current_user,
    )
