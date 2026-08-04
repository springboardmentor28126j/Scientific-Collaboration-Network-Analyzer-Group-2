from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
)

from app.models.user import User

from app.schemas.notification import NotificationResponse

from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "/me",
    response_model=list[NotificationResponse],
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.get_my_notifications(
        db=db,
        current_user=current_user,
    )


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        current_user=current_user,
    )


@router.delete(
    "/{notification_id}",
)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        current_user=current_user,
    )