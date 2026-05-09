from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeCheck API"
    ENVIRONMENT: str = "dev"
    DATABASE_URL: str
    REDIS_URL: str | None = None
    FIREBASE_CREDENTIALS: str | None = None
    CRON_SECRET: str | None = None

    # Rate limiting
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW: int = 60  # seconds

    RATE_LIMIT_SOS_ATTEMPTS: int = 3
    RATE_LIMIT_SOS_WINDOW: int = 60

    RATE_LIMIT_LOST_PHONE_ATTEMPTS: int = 3
    RATE_LIMIT_LOST_PHONE_WINDOW: int = 60

    RATE_LIMIT_SNAPSHOT_ATTEMPTS: int = 10
    RATE_LIMIT_SNAPSHOT_WINDOW: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
