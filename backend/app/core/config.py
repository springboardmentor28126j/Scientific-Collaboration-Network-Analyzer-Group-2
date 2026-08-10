from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Scientific Collaboration Network Analyzer"

    # PostgreSQL is the required backing store. Override via .env, e.g.:
    # postgresql+psycopg://user:password@localhost:5432/scna
    # Uses psycopg v3 (not psycopg2) for Python 3.14 Windows compatibility.
    DATABASE_URL: str = "postgresql+psycopg://scna_user:scna_password@localhost:5432/scna"

    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours, fine for dev/demo

    # Outbound email (collaboration-request notifications, etc.). If
    # SMTP_HOST is left blank, send_email() logs a 'would have sent'
    # warning instead of trying to connect -- lets the app run in dev
    # without real SMTP credentials configured.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = "noreply@scna.local"
    SMTP_FROM_NAME: str = "SCNA"


settings = Settings()
