from fastapi import APIRouter

from app.api.v1 import auth, institution_users, institutions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(institutions.router)
api_router.include_router(institution_users.router)
