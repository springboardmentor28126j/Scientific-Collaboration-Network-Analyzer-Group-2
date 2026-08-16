from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    All values are overridable via environment variables (see .env.example).
    """

    # App
    PROJECT_NAME: str = "Scientific Collaboration Network Analyzer"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/Infosys"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth / JWT
    JWT_SECRET_KEY: str = "iurehrfuireh9w83u98r4hrubguy938rvijfdkjbhruie8gtijfkdjriu48rfhvnrufuiyncreuhgtuerihi"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google Sign-In
    GOOGLE_CLIENT_ID: str = "244237880139-es9h95bv5q4a3hacssvp4c2h6ccc47lo.apps.googleusercontent.com"

    # File storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    LOCAL_STORAGE_PATH: str = "./uploads"
    S3_BUCKET_NAME: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"

    # CORS - Flask frontend origin(s)
    CORS_ORIGINS: list[str] = ["http://localhost:5000"]

    # Email verification
    FRONTEND_BASE_URL: str = "http://localhost:5000"
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # SMTP (used to actually send verification emails)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@scientific-collab-analyzer.local"
    SMTP_USE_TLS: bool = True

    # Email deliverability pre-check (optional -- skipped gracefully if unset)
    ZEROBOUNCE_API_KEY: str = "11085b44e8ca42d6823e246f4dbdbb30"
    EMAIL_DELIVERABILITY_CACHE_TTL_SECONDS: int = 86400

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()