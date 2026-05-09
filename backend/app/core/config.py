from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeCheck API"
    ENVIRONMENT: str = "dev"
    DATABASE_URL: str
    REDIS_URL: str | None = None
    FIREBASE_CREDENTIALS: str | None = None
    CRON_SECRET: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
