import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        notification_type,
        title: str,
        message: str,
        publication_id: uuid.UUID | None = None,
    ) -> Notification:

        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            publication_id=publication_id,
        )

        self.session.add(notification)

        await self.session.flush()

        return notification

    async def create_many(
        self,
        notifications: list[Notification],
    ) -> None:

        self.session.add_all(notifications)

        await self.session.flush()

    async def get_by_id(
        self,
        notification_id: uuid.UUID,
    ) -> Notification | None:

        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notification_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
    ) -> list[Notification]:

        result = await self.session.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
            )
            .order_by(
                Notification.created_at.desc(),
            )
        )

        return list(result.scalars().all())

    async def unread_count(
        self,
        user_id: uuid.UUID,
    ) -> int:

        result = await self.session.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )

        return result.scalar_one()

    async def mark_as_read(
        self,
        notification: Notification,
    ) -> Notification:

        notification.is_read = True

        await self.session.flush()

        return notification

    async def mark_all_as_read(
        self,
        user_id: uuid.UUID,
    ) -> None:

        result = await self.session.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )

        notifications = result.scalars().all()

        for notification in notifications:
            notification.is_read = True

        await self.session.flush()
