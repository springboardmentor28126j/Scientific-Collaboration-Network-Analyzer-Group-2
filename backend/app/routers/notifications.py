from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationOut

router = APIRouter()


@router.post("/", response_model=NotificationOut)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    new_notification = Notification(**notification.dict())
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


@router.get("/", response_model=List[NotificationOut])
def list_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).order_by(Notification.created_at.desc()).limit(20).all()


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.is_read == False).count()
    return {"unread_count": count}


@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.put("/mark-all-read")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}