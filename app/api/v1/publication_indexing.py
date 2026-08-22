import uuid

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.publication_indexing_service import (
    PublicationIndexingService,
)
from app.api.deps import get_publication_indexing_service


router = APIRouter(
    prefix="/publications",
    tags=["Publication AI"],
)


@router.post(
    "/{publication_id}/index",
    summary="Index a published publication",
)
async def index_publication(
    publication_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: PublicationIndexingService = Depends(
        get_publication_indexing_service,
    ),
):
    chunks_created = await service.extract_and_store_chunks(
        publication_id=publication_id,
    )

    return {
        "publication_id": publication_id,
        "status": "INDEXED",
        "chunks_created": chunks_created,
    }
