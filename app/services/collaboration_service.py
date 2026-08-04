from sqlalchemy.orm import Session
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType
from app.repositories.user_repository import UserRepository

from app.models.collaboration import (
    Collaboration,
    CollaborationStatus,
)
from app.repositories.collaboration_repository import (
    CollaborationRepository,
)


class CollaborationService:

    @staticmethod
    def send_request(
        db: Session,
        sender_id,
        receiver_id,
    ):
        collaboration = Collaboration(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status=CollaborationStatus.PENDING,
        )

        collaboration = CollaborationRepository.create(
            db,
            collaboration,
        )

        sender = UserRepository.get_by_id(db, sender_id)

        NotificationService.create_notification(
            db=db,
            user_id=receiver_id,
            title="New Collaboration Request",
            message=f"{sender.email} sent you a collaboration request.",
            notification_type=NotificationType.COLLABORATION,
        )

        return collaboration

    @staticmethod
    def get_pending_requests(
        db: Session,
        receiver_id,
    ):
        return CollaborationRepository.get_pending_requests(
            db,
            receiver_id,
        )

    @staticmethod
    def accept_request(
        db: Session,
        collaboration,
    ):
        collaboration.status = CollaborationStatus.ACCEPTED
        return CollaborationRepository.update(
            db,
            collaboration,
        )

    @staticmethod
    def reject_request(
        db: Session,
        collaboration,
    ):
        collaboration.status = CollaborationStatus.REJECTED
        return CollaborationRepository.update(
            db,
            collaboration,
        )

    @staticmethod
    def get_all(db: Session):
        return CollaborationRepository.get_all(db)