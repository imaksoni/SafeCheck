from app.core.config import settings

def _generate_key(namespace: str, entity: str, id_val: str, purpose: str) -> str:
    """
    Generate a standardized Redis key.
    Format: safewave:{env}:{namespace}:{entity}:{id}:{purpose}
    """
    env = settings.ENVIRONMENT
    return f"safewave:{env}:{namespace}:{entity}:{id_val}:{purpose}"

def get_rate_limit_key(action: str, identifier: str) -> str:
    """Generate a key for rate limiting (e.g., login attempts per IP/user)."""
    return _generate_key("ratelimit", "action", action, identifier)

def get_cache_key(entity: str, id_val: str) -> str:
    """Generate a key for caching database or computation results."""
    return _generate_key("cache", entity, id_val, "data")

def get_idempotency_key(action: str, idempotency_key: str) -> str:
    """Generate a key to ensure operations are idempotent (e.g., preventing duplicate alerts)."""
    return _generate_key("idempotency", "action", action, idempotency_key)

def get_alert_lock_key(session_id: str) -> str:
    """Generate a key for distributed locks on alert creation to prevent race conditions."""
    return _generate_key("lock", "session", session_id, "alert")

def get_device_last_seen_key(device_id: str) -> str:
    """Generate a key for storing the last time a device was seen online."""
    return _generate_key("presence", "device", device_id, "lastseen")
