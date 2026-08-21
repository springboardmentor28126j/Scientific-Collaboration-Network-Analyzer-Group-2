"""
Shared FastAPI dependencies: resolving the current user from a bearer
token, and role-based guards built on top of it.

Per the resolved decision in docs/architecture.md §12: a deactivated
institution must instantly reject its users' requests, even if their JWT
hasn't expired yet. That check lives in get_current_user, below, so it
runs on every authenticated request — not just at login.
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_session
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_error

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise credentials_error from exc

    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise credentials_error

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account email has not been verified",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated",
        )

    # Institution-level kill switch — checked on every request, not just
    # at login, so a deactivated institution instantly locks out an
    # already-issued, still-unexpired access token too.
    if user.institution is not None and not user.institution.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institution has been deactivated",
        )

    return user


def require_roles(*allowed_roles: UserRole):
    """Dependency factory — usage: Depends(require_roles(UserRole.SUPER_ADMIN))"""

    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return _guard


require_superuser = require_roles(UserRole.SUPER_ADMIN)
require_institution_admin = require_roles(UserRole.INSTITUTION_ADMIN)
