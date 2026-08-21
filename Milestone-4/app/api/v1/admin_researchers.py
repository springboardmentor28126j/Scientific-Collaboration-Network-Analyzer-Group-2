from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_superuser
from app.db.session import get_session
from app.models.institution import Institution
from app.models.user import User, UserRole
from app.schemas.user import GlobalResearcherRead

router = APIRouter(prefix="/admin/researchers", tags=["Platform Researchers"])


@router.get("", response_model=list[GlobalResearcherRead], dependencies=[Depends(require_superuser)])
async def list_global_researchers(session: AsyncSession = Depends(get_session)):
    rows = await session.execute(
        select(User, Institution.name)
        .outerjoin(Institution, Institution.id == User.institution_id)
        .where(User.role == UserRole.RESEARCHER)
        .order_by(User.full_name)
    )
    return [GlobalResearcherRead.model_validate(user, from_attributes=True).model_copy(update={"institution_name": institution_name}) for user, institution_name in rows]
