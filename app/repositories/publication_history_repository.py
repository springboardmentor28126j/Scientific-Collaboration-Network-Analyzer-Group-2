import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.publication_history import PublicationHistory
from app.models.user import User


class PublicationHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> PublicationHistory:
        history = PublicationHistory(**fields)
        self.session.add(history)
        await self.session.flush()
        return history

    async def list_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationHistory]:
        result = await self.session.execute(
            select(PublicationHistory)
            .options(
                selectinload(PublicationHistory.user)
            )
            .where(
                PublicationHistory.publication_id == publication_id,
            )
            .order_by(
                PublicationHistory.created_at.desc(),
            )
        )

        return list(result.scalars().all())