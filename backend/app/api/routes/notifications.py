from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationOut, UnreadCountOut

router = APIRouter()

ALLOWED_PAGE_SIZES = {10, 25, 50}


def _unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .count()
    )


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(25),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationListResponse:
    """Every notification for the current user, newest first. Each user
    only ever sees their own notifications (user_id == current_user.id) --
    there's no cross-user visibility, not even for System Admin, since
    these are personal, not an audit/moderation surface."""
    if page_size not in ALLOWED_PAGE_SIZES:
        page_size = 25

    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))

    total = query.count()
    rows = (
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return NotificationListResponse(
        items=[NotificationOut.model_validate(row) for row in rows],
        total=total,
        unread_count=_unread_count(db, current_user.id),
    )


@router.get("/unread-count", response_model=UnreadCountOut)
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UnreadCountOut:
    """Cheap, frequently-polled endpoint for the nav bell badge -- avoids
    pulling the full notification list just to show a number."""
    return UnreadCountOut(unread_count=_unread_count(db, current_user.id))


def _get_own_notification_or_404(db: Session, notification_id: int, user_id: int) -> Notification:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    return notification


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationOut:
    notification = _get_own_notification_or_404(db, notification_id, current_user.id)
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return NotificationOut.model_validate(notification)


@router.post("/mark-all-read", response_model=UnreadCountOut)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UnreadCountOut:
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read.is_(False)
    ).update({Notification.is_read: True})
    db.commit()
    return UnreadCountOut(unread_count=0)
