from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeCheck API"
    DATABASE_URL: str
    FIREBASE_CREDENTIALS: str | None = None
    CRON_SECRET: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
