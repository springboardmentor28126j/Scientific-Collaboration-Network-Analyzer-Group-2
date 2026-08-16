from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, institutions, researchers, publications, conferences, admin, reviews, projects, notifications,
    collaborations, citations, analytics, messages, reports, chatbot,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(institutions.router)
api_router.include_router(researchers.router)
api_router.include_router(publications.router)
api_router.include_router(conferences.router)
api_router.include_router(admin.router)
api_router.include_router(reviews.router)
api_router.include_router(projects.router)
api_router.include_router(notifications.router)
api_router.include_router(collaborations.router)
api_router.include_router(citations.router)
api_router.include_router(analytics.router)
api_router.include_router(messages.router)
api_router.include_router(reports.router)
api_router.include_router(chatbot.router)

# Placeholder for a later milestone:
# api_router.include_router(audit.router)