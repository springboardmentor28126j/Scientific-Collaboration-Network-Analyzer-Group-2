import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication_history import (
    PublicationHistory,
    PublicationHistoryAction,
)
from app.repositories.publication_history_repository import (
    PublicationHistoryRepository,
)

from app.core.exceptions import NotFoundError
from app.repositories.publication_repository import PublicationRepository


class PublicationHistoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.publications = PublicationRepository(session)
        self.history = PublicationHistoryRepository(session)

    async def log(
        self,
        *,
        publication_id: uuid.UUID,
        performed_by: uuid.UUID | None,
        action: PublicationHistoryAction,
        description: str,
    ) -> PublicationHistory:
        """
        Create a publication history entry.
        """

        return await self.history.create(
            publication_id=publication_id,
            performed_by=performed_by,
            action=action,
            description=description,
        )

    async def list_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationHistory]:
        return await self.history.list_by_publication(
            publication_id=publication_id,
        )

    async def get_publication_history(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationHistory]:

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        return await self.history.list_by_publication(
            publication_id,
        )
