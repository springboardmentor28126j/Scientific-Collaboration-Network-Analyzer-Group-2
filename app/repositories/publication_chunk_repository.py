import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication_chunk import PublicationChunk


class PublicationChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(
        self,
        chunks: list[PublicationChunk],
    ) -> None:
        self.session.add_all(chunks)
        await self.session.flush()

    async def delete_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> None:
        await self.session.execute(
            delete(PublicationChunk).where(
                PublicationChunk.publication_id == publication_id,
            )
        )

        await self.session.flush()

    async def list_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationChunk]:
        result = await self.session.execute(
            select(PublicationChunk)
            .where(
                PublicationChunk.publication_id == publication_id,
            )
            .order_by(
                PublicationChunk.page_number.asc(),
                PublicationChunk.chunk_index.asc(),
            )
        )

        return list(result.scalars().all())

    async def count_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> int:
        result = await self.session.execute(
            select(PublicationChunk.id).where(
                PublicationChunk.publication_id == publication_id,
            )
        )

        return len(result.scalars().all())
