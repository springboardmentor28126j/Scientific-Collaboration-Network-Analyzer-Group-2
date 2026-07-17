import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_publication_author_service, get_publication_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.publication import PublicationType
from app.schemas.common import Message
from app.schemas.publication import (
    PublicationCreate,
    PublicationListItem,
    PublicationRead,
    PublicationUpdate,
)
from app.schemas.publication_author import (
    PublicationAuthorCreate,
    PublicationAuthorRead,
)
from app.schemas.publication_decision import (
    PublicationDecisionCreate,
)
from app.services.publication_service import PublicationService
from app.services.publication_author_service import PublicationAuthorService

router = APIRouter(
    prefix="/publications",
    tags=["Publications"],
)


@router.post(
    "",
    response_model=PublicationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new publication",
    description=(
        "Creates a new research publication. Every newly created "
        "publication starts in DRAFT status and is owned by the "
        "currently authenticated researcher."
    ),
)
async def create_publication(
    title: str = Form(...),
    abstract: str = Form(...),
    publication_type: PublicationType = Form(...),
    doi: str | None = Form(None),
    pdf: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    publication_service: PublicationService = Depends(get_publication_service),
):
    payload = PublicationCreate(
        title=title,
        abstract=abstract,
        publication_type=publication_type,
        doi=doi,
    )

    return await publication_service.create_publication(
        payload=payload,
        pdf_file=pdf,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[PublicationListItem],
    summary="List publications",
)
async def list_publications(
    publication_service: PublicationService = Depends(get_publication_service),
):
    return await publication_service.list_publications()


@router.get(
    "/{publication_id}",
    response_model=PublicationRead,
    summary="Get a publication by ID",
)
async def get_publication(
    publication_id: uuid.UUID,
    publication_service: PublicationService = Depends(get_publication_service),
):
    return await publication_service.get_publication(publication_id)


@router.put(
    "/{publication_id}",
    response_model=PublicationRead,
    summary="Update a draft publication",
    description=(
        "Only the creator of the publication can update it, "
        "and only while it is still in DRAFT status."
    ),
)
async def update_publication(
    publication_id: uuid.UUID,
    payload: PublicationUpdate,
    current_user: User = Depends(get_current_user),
    publication_service: PublicationService = Depends(get_publication_service),
):
    return await publication_service.update_publication(
        publication_id=publication_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/{publication_id}",
    response_model=Message,
    summary="Delete a draft publication",
    description=(
        "Deletes a publication. Only the creator may delete it while it remains in DRAFT status."
    ),
)
async def delete_publication(
    publication_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    publication_service: PublicationService = Depends(get_publication_service),
):
    await publication_service.delete_publication(
        publication_id=publication_id,
        current_user=current_user,
    )

    return Message(detail="Publication deleted successfully.")


@router.post(
    "/{publication_id}/authors",
    response_model=PublicationAuthorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a researcher as a co-author",
)
async def add_author(
    publication_id: uuid.UUID,
    payload: PublicationAuthorCreate,
    current_user: User = Depends(get_current_user),
    author_service: PublicationAuthorService = Depends(get_publication_author_service),
):
    return await author_service.add_author(
        publication_id=publication_id,
        payload=payload,
        current_user=current_user,
    )


@router.post(
    "/{publication_id}/authors",
    response_model=PublicationAuthorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a researcher as a co-author",
)
async def add_author(
    publication_id: uuid.UUID,
    payload: PublicationAuthorCreate,
    current_user: User = Depends(get_current_user),
    author_service: PublicationAuthorService = Depends(get_publication_author_service),
):
    return await author_service.add_author(
        publication_id=publication_id,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/{publication_id}/authors",
    response_model=list[PublicationAuthorRead],
    summary="List publication authors",
)
async def list_authors(
    publication_id: uuid.UUID,
    author_service: PublicationAuthorService = Depends(get_publication_author_service),
):
    return await author_service.list_authors(publication_id)


@router.delete(
    "/{publication_id}/authors/{researcher_id}",
    response_model=Message,
    summary="Remove a co-author",
)
async def remove_author(
    publication_id: uuid.UUID,
    researcher_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    author_service: PublicationAuthorService = Depends(get_publication_author_service),
):
    await author_service.remove_author(
        publication_id=publication_id,
        researcher_id=researcher_id,
        current_user=current_user,
    )

    return Message(detail="Author removed successfully.")


@router.post(
    "/{publication_id}/submit",
    response_model=PublicationRead,
    summary="Submit a publication for review",
)
async def submit_publication(
    publication_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    publication_service: PublicationService = Depends(
        get_publication_service,
    ),
):
    return await publication_service.submit_publication(
        publication_id,
        current_user,
    )


@router.post(
    "/{publication_id}/decision",
    response_model=PublicationRead,
    summary="Make editorial decision",
    description=("Super admin only. Accept, reject or request revision for a publication."),
)
async def make_editor_decision(
    publication_id: uuid.UUID,
    payload: PublicationDecisionCreate,
    current_user: User = Depends(get_current_user),
    publication_service: PublicationService = Depends(
        get_publication_service,
    ),
):
    return await publication_service.make_editor_decision(
        publication_id=publication_id,
        payload=payload,
        current_user=current_user,
    )
