from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository


class NotificationService:

    @staticmethod
    def create_notification(
        db: Session,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: NotificationType,
    ):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
        )

        return NotificationRepository.create(
            db,
            notification,
        )

    @staticmethod
    def get_my_notifications(
        db: Session,
        current_user: User,
    ):
        return NotificationRepository.get_by_user_id(
            db,
            current_user.id,
        )

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: UUID,
        current_user: User,
    ):
        notification = NotificationRepository.get_by_id(
            db,
            notification_id,
        )

        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized",
            )

        notification.is_read = True

        return NotificationRepository.update(
            db,
            notification,
        )

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: UUID,
        current_user: User,
    ):
        notification = NotificationRepository.get_by_id(
            db,
            notification_id,
        )

        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized",
            )

        NotificationRepository.delete(
            db,
            notification,
        )

        return {
            "message": "Notification deleted successfully"
        }