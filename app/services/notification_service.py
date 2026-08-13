import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.notification import Notification, NotificationType
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.notifications = NotificationRepository(session)

    async def notify_coauthor_added(
        self,
        *,
        user_id: uuid.UUID,
        publication_id: uuid.UUID,
        publication_title: str,
    ) -> Notification:
        notification = await self.notifications.create(
            user_id=user_id,
            notification_type=NotificationType.COAUTHOR_ADDED,
            title="You were added as a co-author",
            message=(f'You have been added as a co-author to "{publication_title}".'),
            publication_id=publication_id,
        )

        return notification

    async def notify_reviewer_assigned(
        self,
        *,
        user_id: uuid.UUID,
        publication_id: uuid.UUID,
        publication_title: str,
    ) -> Notification:
        notification = await self.notifications.create(
            user_id=user_id,
            notification_type=NotificationType.REVIEW_ASSIGNED,
            title="New review assigned",
            message=(f'You have been assigned to review "{publication_title}".'),
            publication_id=publication_id,
        )

        return notification

    async def notify_publication_published(
        self,
        *,
        user_ids: list[uuid.UUID],
        publication_id: uuid.UUID,
        publication_title: str,
    ) -> None:
        notifications = [
            Notification(
                user_id=user_id,
                notification_type=NotificationType.PUBLICATION_PUBLISHED,
                title="Publication published",
                message=(f'"{publication_title}" has been published.'),
                publication_id=publication_id,
            )
            for user_id in user_ids
        ]

        if notifications:
            await self.notifications.create_many(notifications)

    async def notify_conference_created(
        self,
        *,
        user_ids: list[uuid.UUID],
        publication_id: uuid.UUID,
        publication_title: str,
    ) -> None:
        notifications = [
            Notification(
                user_id=user_id,
                notification_type=NotificationType.CONFERENCE_CREATED,
                title="Conference information added",
                message=(f'Conference information has been added to "{publication_title}".'),
                publication_id=publication_id,
            )
            for user_id in user_ids
        ]

        if notifications:
            await self.notifications.create_many(notifications)

    async def list_notifications(
        self,
        user_id: uuid.UUID,
    ):
        return await self.notifications.list_for_user(user_id)

    async def unread_count(
        self,
        user_id: uuid.UUID,
    ):
        return await self.notifications.unread_count(user_id)

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        notification = await self.notifications.get_by_id(
            notification_id,
        )

        if notification is None:
            raise NotFoundError("Notification not found.")

        if notification.user_id != user_id:
            raise ForbiddenError("You can only access your own notifications.")

        notification = await self.notifications.mark_as_read(
            notification,
        )

        await self.session.commit()

        await self.session.refresh(notification)

        return notification

    async def mark_all_as_read(
        self,
        user_id: uuid.UUID,
    ):
        await self.notifications.mark_all_as_read(
            user_id,
        )

        await self.session.commit()
