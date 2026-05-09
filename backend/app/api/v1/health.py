from fastapi import APIRouter
from app.core import redis

router = APIRouter()

@router.get("/health")
async def health_check():
    redis_status = "unconfigured"
    if redis.redis_client:
        try:
            await redis.redis_client.ping()
            redis_status = "ok"
        except Exception:
            redis_status = "unhealthy"

    return {"status": "ok", "message": "Healthy", "redis": redis_status}
