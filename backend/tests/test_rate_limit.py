import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.core.rate_limit import AnonymousRateLimiter, UserRateLimiter
from app.models.user import User
from app.core import redis

@pytest.fixture
def mock_redis_pipeline():
    with patch("app.core.redis.redis_client") as mock_client:
        mock_pipe = AsyncMock()
        mock_client.pipeline.return_value = mock_pipe
        yield mock_pipe, mock_client

@pytest.mark.asyncio
async def test_anonymous_rate_limiter_allowed(mock_redis_pipeline):
    mock_pipe, mock_client = mock_redis_pipeline
    # current_count = 1, ttl = -1
    mock_pipe.execute.return_value = (1, -1)

    limiter = AnonymousRateLimiter("test_action", 5, 60)

    class MockRequest:
        class MockClient:
            host = "127.0.0.1"
        client = MockClient()

    request = MockRequest()

    # Should not raise exception
    await limiter(request)

    # Check that expire was called since current_count == 1
    mock_client.expire.assert_called_once_with("safewave:dev:ratelimit:action:test_action:127.0.0.1", 60)

@pytest.mark.asyncio
async def test_anonymous_rate_limiter_blocked(mock_redis_pipeline):
    mock_pipe, mock_client = mock_redis_pipeline
    # current_count = 6 (exceeds limit 5), ttl = 30
    mock_pipe.execute.return_value = (6, 30)

    limiter = AnonymousRateLimiter("test_action", 5, 60)

    class MockRequest:
        class MockClient:
            host = "127.0.0.1"
        client = MockClient()

    request = MockRequest()

    with pytest.raises(HTTPException) as exc_info:
        await limiter(request)

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"] == "30"

@pytest.mark.asyncio
async def test_user_rate_limiter_blocked(mock_redis_pipeline):
    mock_pipe, mock_client = mock_redis_pipeline
    # current_count = 4 (exceeds limit 3), ttl = 45
    mock_pipe.execute.return_value = (4, 45)

    limiter = UserRateLimiter("sos", 3, 60)

    user = User(id=99, firebase_uid="test_uid")

    with pytest.raises(HTTPException) as exc_info:
        await limiter(user)

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"] == "45"

@pytest.mark.asyncio
async def test_rate_limiter_fail_open_when_redis_none():
    with patch("app.core.redis.redis_client", None):
        limiter = AnonymousRateLimiter("test_action", 5, 60)

        class MockRequest:
            class MockClient:
                host = "127.0.0.1"
            client = MockClient()

        request = MockRequest()

        # Should not raise exception even if Redis is missing
        await limiter(request)

@pytest.mark.asyncio
async def test_rate_limiter_fail_open_on_redis_error(mock_redis_pipeline):
    mock_pipe, mock_client = mock_redis_pipeline
    # Simulate Redis connection error
    mock_pipe.execute.side_effect = Exception("Redis connection failed")

    limiter = UserRateLimiter("sos", 3, 60)
    user = User(id=99, firebase_uid="test_uid")

    # Should not raise exception
    await limiter(user)
