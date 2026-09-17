from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# Create Notification
@router.post("/")
def create_notification(
    user_id: int,
    message: str,
    notification_type: str = "General",
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    notification = models.Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        is_read=0
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# Get All Notifications
@router.get("/")
def get_notifications(
    db: Session = Depends(get_db)
):
    return db.query(models.Notification).all()


# Get Notifications for a User
@router.get("/user/{user_id}")
def get_user_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).all()


# Mark Notification as Read
@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.query(models.Notification).filter(
        models.Notification.notification_id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = 1

    db.commit()
    db.refresh(notification)

    return notification


# Delete Notification
@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.query(models.Notification).filter(
        models.Notification.notification_id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {
        "message": "Notification deleted successfully"
    }