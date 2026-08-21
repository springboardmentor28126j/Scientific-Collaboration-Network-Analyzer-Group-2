"""
Creates the platform superuser from .env values on startup, if it doesn't
already exist. This is the *only* way a SUPER_ADMIN account is ever
created — there is no API endpoint for it, by design.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


async def bootstrap_superuser(session: AsyncSession) -> None:
    repo = UserRepository(session)
    existing = await repo.get_by_email(settings.SUPERUSER_EMAIL)
    if existing is not None:
        logger.info("Superuser already exists — skipping bootstrap.")
        return

    await repo.create(
        email=settings.SUPERUSER_EMAIL,
        hashed_password=hash_password(settings.SUPERUSER_PASSWORD),
        full_name=settings.SUPERUSER_FULL_NAME,
        role=UserRole.SUPER_ADMIN,
        institution_id=None,
        is_verified=True,
        is_active=True,
    )
    await session.commit()
    logger.info("Superuser bootstrapped from .env: %s", settings.SUPERUSER_EMAIL)
