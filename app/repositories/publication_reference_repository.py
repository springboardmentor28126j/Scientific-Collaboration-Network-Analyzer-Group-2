import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication_reference import PublicationReference


class PublicationReferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        **fields,
    ) -> PublicationReference:
        reference = PublicationReference(**fields)

        self.session.add(reference)

        await self.session.flush()

        return reference

    async def get_by_id(
        self,
        reference_id: uuid.UUID,
    ) -> PublicationReference | None:

        result = await self.session.execute(
            select(PublicationReference).where(PublicationReference.id == reference_id)
        )

        return result.scalar_one_or_none()

    async def list_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationReference]:

        result = await self.session.execute(
            select(PublicationReference)
            .where(PublicationReference.publication_id == publication_id)
            .order_by(PublicationReference.reference_order.asc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        reference: PublicationReference,
        **fields,
    ) -> PublicationReference:

        for key, value in fields.items():
            setattr(reference, key, value)

        await self.session.flush()

        return reference

    async def delete(
        self,
        reference: PublicationReference,
    ) -> None:

        await self.session.delete(reference)

        await self.session.flush()

    async def next_reference_order(
        self,
        publication_id: uuid.UUID,
    ) -> int:

        result = await self.session.execute(
            select(func.max(PublicationReference.reference_order)).where(
                PublicationReference.publication_id == publication_id
            )
        )

        max_order = result.scalar_one()

        if max_order is None:
            return 1

        return max_order + 1
