from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, institutions, researchers, publications, conferences

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(institutions.router)
api_router.include_router(researchers.router)
api_router.include_router(publications.router)
api_router.include_router(conferences.router)

# Placeholders for later milestones (Milestone 2-3):
# api_router.include_router(collaborations.router)
# api_router.include_router(citations.router)
# api_router.include_router(reports.router)
# api_router.include_router(audit.router)
