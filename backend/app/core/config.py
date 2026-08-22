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


settings = Settings()
