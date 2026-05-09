import logging
from typing import AsyncGenerator
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client instance
redis_client: redis.Redis | None = None

async def init_redis() -> None:
    """Initialize the Redis connection pool."""
    global redis_client
    if settings.REDIS_URL:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            redis_client = None
    else:
        logger.info("REDIS_URL not set, Redis client will not be initialized")

async def close_redis() -> None:
    """Close the Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
        logger.info("Closed Redis connection")

async def get_redis() -> AsyncGenerator[redis.Redis | None, None]:
    """Dependency to get the Redis client."""
    yield redis_client
