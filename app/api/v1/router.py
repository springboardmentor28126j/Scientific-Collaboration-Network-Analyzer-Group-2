from fastapi import APIRouter

from app.api.v1 import (
    auth,
    institution_users,
    institutions,
    review_assignments,
    users,
    publications,
    reviews,
    publication_history,
    publication_conference,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(institutions.router)
api_router.include_router(institution_users.router)
api_router.include_router(publications.router)
api_router.include_router(users.router)
api_router.include_router(review_assignments.router)
api_router.include_router(reviews.router)
api_router.include_router(publication_history.router)
api_router.include_router(publication_conference.router)
