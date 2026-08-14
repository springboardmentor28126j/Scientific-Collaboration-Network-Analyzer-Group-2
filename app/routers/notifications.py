from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.models import Notification

from app.schemas import (
    NotificationCreate,
    NotificationResponse
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# Create Notification
@router.post(
    "/",
    response_model=NotificationResponse
)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):

    return crud.create_notification(
        db,
        notification
    )


# Get all notifications for a user
@router.get(
    "/{user_id}",
    response_model=list[NotificationResponse]
)
def get_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_user_notifications(
        db,
        user_id
    )


# Get unread notification count
@router.get("/unread-count/{user_id}")
def unread_notification_count(
    user_id: int,
    db: Session = Depends(get_db)
):

    count = db.query(Notification).filter(
        Notification.receiver_id == user_id,
        Notification.is_read == False
    ).count()

    return {
        "count": count
    }

# Mark notification as read
@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):

    return crud.mark_notification_read(
        db,
        notification_id
    )