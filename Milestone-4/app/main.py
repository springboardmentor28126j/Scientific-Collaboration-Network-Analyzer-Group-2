"""
Application factory: creates the FastAPI instance, registers routers,
middleware, exception handlers, and the startup-time superuser bootstrap.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.db.base import Base
from app.db.init_db import bootstrap_superuser
from app.db.session import AsyncSessionLocal, engine
from app.middleware.logging_middleware import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Docker and production use Alembic/PostgreSQL.  For a self-contained
    # local run, SQLite can initialize the same SQLAlchemy metadata directly.
    if engine.url.get_backend_name() == "sqlite":
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await bootstrap_superuser(session)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "Backend for the Scientific Research Management System — "
            "authentication and institution/user management module."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(
            dict.fromkeys([*settings.BACKEND_CORS_ORIGINS, "http://127.0.0.1:3000"])
        ),
        allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(
        _request: Request, exc: ValidationError
    ) -> JSONResponse:
        """
        Handles pydantic ValidationError raised when a schema is
        constructed manually inside a route (e.g. InstitutionRegister,
        built from multipart Form(...) fields rather than a JSON body
        FastAPI validates automatically). Mirrors FastAPI's own 422 shape
        so API consumers see one consistent validation error format.
        """
        errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": errors})

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Health"], summary="Liveness/readiness probe")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
