from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationOut, UnreadCountOut

router = APIRouter()


def create_notification(
    db: Session,
    recipient_user_id: int,
    type: str,
    message: str,
    link: str | None = None,
    also_email: bool = False,
) -> Notification:
    """Call this directly from other route files (collaborations, reviewer
    assignments, publications) right before their own db.commit() -- or
    call db.commit() again after, either is fine since this only adds a row."""
    notification = Notification(
        recipient_user_id=recipient_user_id, type=type, message=message, link=link
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationListResponse:
    query = db.query(Notification).filter(Notification.recipient_user_id == current_user.id)
    total = query.count()
    unread_count = query.filter(Notification.is_read.is_(False)).count()
    items = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return NotificationListResponse(items=items, total=total, unread_count=unread_count)


@router.get("/unread-count", response_model=UnreadCountOut)
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UnreadCountOut:
    count = (
        db.query(Notification)
        .filter(Notification.recipient_user_id == current_user.id, Notification.is_read.is_(False))
        .count()
    )
    return UnreadCountOut(unread_count=count)


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Notification:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.recipient_user_id == current_user.id)
        .first()
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/mark-all-read", response_model=UnreadCountOut)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UnreadCountOut:
    (
        db.query(Notification)
        .filter(Notification.recipient_user_id == current_user.id, Notification.is_read.is_(False))
        .update({"is_read": True})
    )
    db.commit()
    return UnreadCountOut(unread_count=0)