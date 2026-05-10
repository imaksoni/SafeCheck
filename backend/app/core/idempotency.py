import hashlib
import json
import logging
from typing import Optional, Any, Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core import redis
from app.core.redis_keys import get_idempotency_key

logger = logging.getLogger(__name__)

class IdempotencyConflictException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class IdempotencyManager:
    """
    Manages best-effort, time-bounded idempotency for API endpoints.

    Behavior:
    - Atomically claims an idempotency key as "in_progress".
    - If a matching completed response exists, returns it.
    - If a request is already in progress, raises a conflict.
    - Re-using a key with a different payload hash raises a conflict.

    Limitations:
    - If Redis is unavailable, this fails open (proceeds without idempotency).
    - PostgreSQL remains the source of truth; this is merely deduplication protection.
    """
    def __init__(self, action: str, ttl_seconds: int = 86400):
        self.action = action
        self.ttl_seconds = ttl_seconds

    def _hash_payload(self, payload: Any) -> str:
        payload_str = json.dumps(jsonable_encoder(payload), sort_keys=True)
        return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    async def check_and_lock(self, idempotency_key: str, user_id: int, payload: Any) -> Optional[Dict]:
        """
        Attempts to lock the idempotency key.
        Returns a cached response dictionary if it was already completed successfully.
        Raises IdempotencyConflictException if in progress or payload mismatch.
        """
        if not redis.redis_client:
            return None

        key = get_idempotency_key(self.action, f"{user_id}:{idempotency_key}")
        payload_hash = self._hash_payload(payload)

        try:
            cached_data = await redis.redis_client.get(key)
            if cached_data:
                data = json.loads(cached_data)

                if data.get("payload_hash") != payload_hash:
                    raise IdempotencyConflictException("Idempotency key already used with a different payload")

                if data.get("status") == "in_progress":
                    raise IdempotencyConflictException("Request is already in progress")

                if data.get("status") == "completed":
                    return data.get("response")

            # Try to set as in_progress
            in_progress_data = {
                "status": "in_progress",
                "payload_hash": payload_hash
            }

            acquired = await redis.redis_client.set(
                key,
                json.dumps(in_progress_data),
                nx=True,
                ex=300 # 5 minute lock for in-progress
            )

            if not acquired:
                # Someone else acquired it right before us
                raise IdempotencyConflictException("Request is already in progress")

            return None

        except IdempotencyConflictException:
            raise
        except Exception as e:
            logger.error(f"Idempotency check_and_lock error: {e}")
            return None

    async def save_success(self, idempotency_key: str, user_id: int, payload: Any, response_data: Any) -> None:
        """Saves the successful response to Redis."""
        if not redis.redis_client:
            return

        key = get_idempotency_key(self.action, f"{user_id}:{idempotency_key}")
        payload_hash = self._hash_payload(payload)

        try:
            completed_data = {
                "status": "completed",
                "payload_hash": payload_hash,
                "response": jsonable_encoder(response_data)
            }
            await redis.redis_client.set(key, json.dumps(completed_data), ex=self.ttl_seconds)
        except Exception as e:
            logger.error(f"Idempotency save_success error: {e}")

    async def unlock(self, idempotency_key: str, user_id: int) -> None:
        """Releases the lock on failure so the client can retry."""
        if not redis.redis_client:
            return

        key = get_idempotency_key(self.action, f"{user_id}:{idempotency_key}")
        try:
            await redis.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Idempotency unlock error: {e}")
