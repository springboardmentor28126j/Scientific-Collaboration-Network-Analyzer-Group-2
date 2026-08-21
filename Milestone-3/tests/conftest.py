"""
Shared pytest fixtures.

Uses an in-memory SQLite DB (async, via aiosqlite) instead of the Postgres
from docker-compose.test.yml, so the test suite is fast and has zero
external dependencies to run in CI. The auth/institution logic exercised
here is plain CRUD + business rules with no Postgres-specific behavior.

Cloudinary and email sending are patched at the service level so tests
never hit real external services. The email mocks are exposed to tests so
they can pull the raw verification/reset token out of the "sent" link and
drive the full verify/reset flow end-to-end.
"""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registers all tables on Base.metadata)
from app.db.base import Base
from app.db.session import get_session
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with patch(
        "app.services.institution_service.CloudinaryService.upload_institution_logo",
        new=AsyncMock(return_value=("https://cdn.example.com/logo.png", "fake_public_id")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def email_mocks() -> AsyncGenerator[dict, None]:
    with (
        patch(
            "app.services.email_service.EmailService.send_institution_verification_email",
            new=AsyncMock(),
        ) as inst,
        patch(
            "app.services.email_service.EmailService.send_invite_verification_email",
            new=AsyncMock(),
        ) as invite,
        patch(
            "app.services.email_service.EmailService.send_password_reset_email",
            new=AsyncMock(),
        ) as reset,
    ):
        yield {"institution": inst, "invite": invite, "reset": reset}


def extract_token(link: str) -> str:
    """Pulls the `token=...` query param out of a link embedded in a
    mocked email call, e.g. 'http://.../verify-email?token=abc123'."""
    return link.split("token=", 1)[1]
