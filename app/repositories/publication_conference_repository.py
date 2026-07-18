from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication
from app.models.publication_conference import PublicationConference


class PublicationConferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> PublicationConference:
        conference = PublicationConference(**fields)
        self.session.add(conference)
        await self.session.flush()
        return conference

    async def get_by_publication(
        self,
        publication_id,
    ) -> PublicationConference | None:
        stmt = select(PublicationConference).where(
            PublicationConference.publication_id == publication_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def update(
        self,
        conference: PublicationConference,
        **fields,
    ) -> PublicationConference:
        for key, value in fields.items():
            setattr(conference, key, value)

        await self.session.flush()

        return conference

    async def delete(
        self,
        conference: PublicationConference,
    ) -> None:
        await self.session.delete(conference)
        await self.session.flush()
