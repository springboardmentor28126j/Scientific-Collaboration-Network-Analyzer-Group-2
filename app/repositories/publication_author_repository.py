import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.publication_author import PublicationAuthor
from app.models.user import User


class PublicationAuthorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> PublicationAuthor:
        author = PublicationAuthor(**fields)
        self.session.add(author)
        await self.session.flush()
        return author

    async def list_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationAuthor]:
        result = await self.session.execute(
            select(PublicationAuthor)
            .options(selectinload(PublicationAuthor.researcher).selectinload(User.institution))
            .where(PublicationAuthor.publication_id == publication_id)
            .order_by(PublicationAuthor.author_order.asc())
        )
        return list(result.scalars().all())

    async def get_author(
        self,
        publication_id: uuid.UUID,
        researcher_id: uuid.UUID,
    ) -> PublicationAuthor | None:
        result = await self.session.execute(
            select(PublicationAuthor).where(
                PublicationAuthor.publication_id == publication_id,
                PublicationAuthor.researcher_id == researcher_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_author_order(
        self,
        publication_id: uuid.UUID,
        author_order: int,
    ) -> PublicationAuthor | None:
        result = await self.session.execute(
            select(PublicationAuthor).where(
                PublicationAuthor.publication_id == publication_id,
                PublicationAuthor.author_order == author_order,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, author: PublicationAuthor) -> None:
        await self.session.delete(author)
        await self.session.flush()
