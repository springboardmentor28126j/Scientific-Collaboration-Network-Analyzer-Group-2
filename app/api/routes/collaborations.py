from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
)

from app.models.collaboration import Collaboration
from app.repositories.collaboration_repository import CollaborationRepository
from app.schemas.collaborations import CollaborationCreate
from app.services.collaboration_service import CollaborationService

router = APIRouter(
    prefix="/collaborations",
    tags=["Collaborations"],
)


# Send Collaboration Request
@router.post("/request")
def send_request(
    data: CollaborationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CollaborationService.send_request(
        db,
        current_user.id,
        data.receiver_id,
    )


# Get All Collaborations
@router.get("/")
def get_all_collaborations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CollaborationService.get_all(db)


# Get Pending Requests
@router.get("/pending")
def get_pending_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CollaborationService.get_pending_requests(
        db,
        current_user.id,
    )


# Accept Collaboration Request
@router.put("/{collaboration_id}/accept")
def accept_request(
    collaboration_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    collaboration = CollaborationRepository.get_by_id(
        db,
        collaboration_id,
    )

    if collaboration is None:
        raise HTTPException(
            status_code=404,
            detail="Collaboration request not found",
        )

    return CollaborationService.accept_request(
        db,
        collaboration,
    )


# Reject Collaboration Request
@router.put("/{collaboration_id}/reject")
def reject_request(
    collaboration_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    collaboration = CollaborationRepository.get_by_id(
        db,
        collaboration_id,
    )

    if collaboration is None:
        raise HTTPException(
            status_code=404,
            detail="Collaboration request not found",
        )

    return CollaborationService.reject_request(
        db,
        collaboration,
    )