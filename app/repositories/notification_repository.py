from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:

    @staticmethod
    def create(db: Session, notification: Notification):
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_by_id(
        db: Session,
        notification_id: UUID,
    ):
        return (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

    @staticmethod
    def get_by_user_id(
        db: Session,
        user_id: UUID,
    ):
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def get_unread_by_user_id(
        db: Session,
        user_id: UUID,
    ):
        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        notification: Notification,
    ):
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def delete(
        db: Session,
        notification: Notification,
    ):
        db.delete(notification)
        db.commit()