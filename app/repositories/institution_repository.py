import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.institution import Institution


class InstitutionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> Institution:
        institution = Institution(**fields)
        self.session.add(institution)
        await self.session.flush()
        return institution

    async def list_all(self) -> list[Institution]:
        result = await self.session.execute(
            select(Institution).order_by(Institution.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, institution_id: uuid.UUID) -> Institution | None:
        result = await self.session.execute(
            select(Institution).where(Institution.id == institution_id)
        )
        return result.scalar_one_or_none()

    async def set_active(self, institution: Institution, is_active: bool) -> Institution:
        institution.is_active = is_active
        await self.session.flush()
        return institution
