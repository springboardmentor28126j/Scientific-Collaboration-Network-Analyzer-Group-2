"""
Application settings, loaded from environment variables / .env file.

Everything the app needs to configure itself lives here. Never hardcode
secrets, URLs, or credentials anywhere else in the codebase — import
`settings` from this module instead.
"""

from functools import lru_cache

from pydantic import EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "Scientific Research Management System"
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    TURNSTILE_SECRET_KEY: str

    # --- Database ---
    DATABASE_URL: str

    # --- Superuser bootstrap ---
    SUPERUSER_EMAIL: EmailStr
    SUPERUSER_PASSWORD: str
    SUPERUSER_FULL_NAME: str = "Platform Super Admin"

    # --- Cloudinary ---
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # --- Mail ---
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: EmailStr = "noreply@platform.com"
    MAIL_FROM_NAME: str = "Research Management System"
    MAIL_SERVER: str = "mailcatcher"
    MAIL_PORT: int = 1025
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = False
    MAIL_VALIDATE_CERTS: bool = False

    # --- Frontend ---
    FRONTEND_URL: str = "http://localhost:3000"

    # --- CORS ---
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("DATABASE_URL")
    @classmethod
    def ensure_async_driver(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            # Guard against accidentally using the sync driver string.
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — env is only read once per process."""
    return Settings()


settings = get_settings()
