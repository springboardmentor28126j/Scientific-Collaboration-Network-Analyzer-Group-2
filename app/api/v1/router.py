from fastapi import APIRouter

from app.api.v1 import admin_researchers, auth, departments, institution_users, institutions, reports, research

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admin_researchers.router)
api_router.include_router(institutions.router)
api_router.include_router(institution_users.router)
api_router.include_router(departments.router)
api_router.include_router(research.router)
api_router.include_router(reports.router)
