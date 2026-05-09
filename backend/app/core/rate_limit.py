import logging
from typing import Callable, Any
from fastapi import Request, HTTPException, status, Depends

from app.core import redis
from app.core.redis_keys import get_rate_limit_key
from app.api.deps import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

async def _check_rate_limit(action: str, identifier: str, limit: int, window: int) -> None:
    """Internal helper to check and increment rate limit in Redis."""
    if not redis.redis_client:
        return  # Allow if Redis is not configured or down

    key = get_rate_limit_key(action, identifier)

    try:
        pipe = redis.redis_client.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        current_count, ttl = await pipe.execute()

        if current_count == 1 or ttl == -1:
            # Set expiry on first request
            await redis.redis_client.expire(key, window)
            ttl = window

        if current_count > limit:
            retry_after = ttl if ttl > 0 else window
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={"Retry-After": str(retry_after)}
            )
    except HTTPException:
        raise
    except Exception as e:
        # Log error but fail open (don't block requests if Redis fails)
        logger.error(f"Rate limiting error: {e}")

class AnonymousRateLimiter:
    """Rate limiter based on client IP. Used for anonymous routes like login."""
    def __init__(self, action: str, limit: int, window: int):
        self.action = action
        self.limit = limit
        self.window = window

    async def __call__(self, request: Request) -> None:
        identifier = request.client.host if request.client else "unknown"
        await _check_rate_limit(self.action, identifier, self.limit, self.window)

class UserRateLimiter:
    """Rate limiter based on authenticated user ID. Used for protected routes."""
    def __init__(self, action: str, limit: int, window: int):
        self.action = action
        self.limit = limit
        self.window = window

    async def __call__(self, current_user: User = Depends(get_current_user)) -> None:
        identifier = str(current_user.id)
        await _check_rate_limit(self.action, identifier, self.limit, self.window)
