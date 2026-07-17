from datetime import UTC, datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import publication, PublicationStatus
from app.models.publication import Publication, PublicationStatus


class PublicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> Publication:
        publication = Publication(**fields)
        self.session.add(publication)
        await self.session.flush()
        return publication

    async def get_by_id(self, publication_id: uuid.UUID) -> Publication | None:
        result = await self.session.execute(
            select(Publication).where(Publication.id == publication_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Publication]:
        result = await self.session.execute(
            select(Publication).order_by(Publication.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, publication: Publication, **fields) -> Publication:
        for key, value in fields.items():
            setattr(publication, key, value)

        await self.session.flush()
        return publication

    async def delete(self, publication: Publication) -> None:
        await self.session.delete(publication)
        await self.session.flush()

    async def get_by_doi(self, doi: str) -> Publication | None:
        result = await self.session.execute(select(Publication).where(Publication.doi == doi))
        return result.scalar_one_or_none()

    async def submit(self, publication: Publication) -> Publication:
        publication.status = PublicationStatus.SUBMITTED
        publication.submitted_at = datetime.now(UTC)

        await self.session.flush()
        return publication

    async def update_editor_decision(
        self,
        publication: Publication,
        status: PublicationStatus,
        editor_note: str,
        decided_by: uuid.UUID,
    ) -> Publication:

        publication.status = status
        publication.editor_note = editor_note
        publication.decided_by = decided_by
        publication.decision_at = datetime.now(UTC)

        await self.session.flush()

        return publication
    
    async def publish(
        self,
        publication: Publication,
    ) -> Publication:
        publication.status = PublicationStatus.PUBLISHED
        publication.published_at = datetime.now(timezone.utc)

        await self.session.flush()

        return publication
    
    async def archive(
        self,
        publication: Publication,
    ) -> Publication:
        publication.status = PublicationStatus.ARCHIVED
        publication.archived_at = datetime.now(timezone.utc)

        await self.session.flush()

        return publication
