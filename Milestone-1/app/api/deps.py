"""
Wiring between routes and services. Routes depend on these factories
rather than importing services directly, so tests can override them
cleanly via FastAPI's dependency_overrides.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.auth_service import AuthService
from app.services.institution_service import InstitutionService
from app.services.user_service import UserService


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


def get_institution_service(session: AsyncSession = Depends(get_session)) -> InstitutionService:
    return InstitutionService(session)


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)
