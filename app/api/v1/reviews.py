import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_review_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead
from app.services.review_service import ReviewService

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


@router.post(
    "",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review",
    description=("Reviewer only. Submit a review for an assigned publication."),
)
async def submit_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.submit_review(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Get review details",
)
async def get_review(
    review_id: uuid.UUID,
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.get_review(review_id)


@router.get(
    "/publication/{publication_id}",
    response_model=list[ReviewRead],
    summary="List all reviews for a publication",
)
async def list_publication_reviews(
    publication_id: uuid.UUID,
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.list_publication_reviews(publication_id)
