import uuid

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationRead
from app.services.notification_service import NotificationService
from app.api.deps import get_notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationRead],
    summary="Get my notifications",
)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    return await service.list_notifications(
        user_id=current_user.id,
    )


@router.get(
    "/unread-count",
    response_model=int,
    summary="Get unread notification count",
)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    return await service.unread_count(
        user_id=current_user.id,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationRead,
    summary="Mark notification as read",
)
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    return await service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )


@router.patch(
    "/read-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark all notifications as read",
)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    await service.mark_all_as_read(
        user_id=current_user.id,
    )
