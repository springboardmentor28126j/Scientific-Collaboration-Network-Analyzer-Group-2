from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.notification_service import email_recipients, is_resend_configured, notify_users
from app.audit import record as record_audit

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _require_admin(token: str, db: Session) -> models.User:
    user_id = auth.read_token_subject(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role.lower() not in {"admin", "system admin"}:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access is required")
    return user


@router.get("/recipients")
def get_recipients(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    administrator = _require_admin(token, db)
    users = [{"key": f"user:{user.id}", "name": user.name, "email": user.email, "role": user.role, "kind": "User account"} for user in db.query(models.User).order_by(models.User.name).all()]
    researchers = [{"key": f"researcher:{researcher.id}", "name": researcher.full_name, "email": researcher.email, "role": researcher.designation or "Researcher", "kind": "Researcher contact"} for researcher in db.query(models.Researcher).filter(models.Researcher.email.isnot(None)).order_by(models.Researcher.full_name).all()]
    return users + researchers


@router.post("/announcement")
def send_announcement(announcement: schemas.AnnouncementCreate, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    administrator = _require_admin(token, db)
    requested = announcement.recipient_ids or []
    if requested:
        user_ids = [int(value.split(":", 1)[1]) for value in requested if value.startswith("user:")]
        researcher_ids = [int(value.split(":", 1)[1]) for value in requested if value.startswith("researcher:")]
        users = db.query(models.User).filter(models.User.id.in_(user_ids)).all() if user_ids else []
        researchers = db.query(models.Researcher).filter(models.Researcher.id.in_(researcher_ids), models.Researcher.email.isnot(None)).all() if researcher_ids else []
    else:
        users = db.query(models.User).all()
        researchers = db.query(models.Researcher).filter(models.Researcher.email.isnot(None)).all()
    if not users and not researchers:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Choose at least one recipient")
    user_emails_sent = notify_users(db, users, notification_type="announcement", title=announcement.title, message=announcement.message, link=announcement.link, email=announcement.send_email) if users else 0
    emails_sent = email_recipients([researcher.email for researcher in researchers], title=announcement.title, message=announcement.message, link=announcement.link) if announcement.send_email else 0
    record_audit(db, action="sent", entity_type="announcement", user_id=administrator.id, details=f"Recipients: {len(users) + len(researchers)}; title: {announcement.title}")
    return {"message": "Announcement sent", "recipient_count": len(users) + len(researchers), "in_app_count": len(users), "email_requested": announcement.send_email, "email_configured": is_resend_configured(), "email_accepted_count": user_emails_sent + emails_sent}


@router.get("/")
def get_notifications(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    user_id = auth.read_token_subject(token)
    records = db.query(models.Notification).filter(models.Notification.user_id == user_id, models.Notification.is_read == 0).order_by(models.Notification.created_at.desc()).limit(20).all()
    return {"notifications": [{"id": item.id, "type": item.type, "title": item.title, "message": item.message, "link": item.link, "is_read": bool(item.is_read), "created_at": item.created_at} for item in records], "count": sum(not item.is_read for item in records)}


@router.post("/{notification_id}/read")
def mark_as_read(notification_id: int, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    user_id = auth.read_token_subject(token)
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id, models.Notification.user_id == user_id).first()
    if not notification:
        return {"message": "Notification not found"}
    notification.is_read = 1
    db.commit()
    return {"message": "Notification marked as read"}


@router.post("/read-all")
def mark_all_as_read(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    user_id = auth.read_token_subject(token)
    db.query(models.Notification).filter(models.Notification.user_id == user_id, models.Notification.is_read == 0).update({models.Notification.is_read: 1})
    db.commit()
    return {"message": "All notifications marked as read"}
