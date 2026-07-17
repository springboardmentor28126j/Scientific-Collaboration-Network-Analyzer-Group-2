import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.publication_history import PublicationHistoryRead
from app.services.publication_history_service import (
    PublicationHistoryService,
)

router = APIRouter(
    prefix="/publications",
    tags=["Publication History"],
)


def get_publication_history_service(
    session: AsyncSession = Depends(get_session),
) -> PublicationHistoryService:
    return PublicationHistoryService(session)


@router.get(
    "/{publication_id}/history",
    response_model=list[PublicationHistoryRead],
    summary="Get publication history",
)
async def get_publication_history(
    publication_id: uuid.UUID,
    service: PublicationHistoryService = Depends(
        get_publication_history_service,
    ),
):
    return await service.get_publication_history(
        publication_id,
    )
