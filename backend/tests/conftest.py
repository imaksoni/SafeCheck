import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_current_user
from app.db.session import get_db, Base
from app.models import *  # Ensure all models are loaded

# Setup in-memory sqlite db for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

from unittest.mock import AsyncMock

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis client globally so idempotency and rate limits pass/fail deterministically"""
    from app.core import redis

    # Store old client
    old_client = redis.redis_client

    class MockRedisClient:
        def __init__(self):
            self.store = {}
            self.ttl_store = {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, value, nx=False, ex=None):
            if nx and key in self.store:
                return False
            self.store[key] = value
            self.ttl_store[key] = ex
            return True

        async def delete(self, key):
            if key in self.store:
                del self.store[key]

        def pipeline(self):
            class MockPipeline:
                def __init__(self, parent):
                    self.parent = parent
                    self.key = None
                def incr(self, key):
                    self.key = key
                    return self
                def ttl(self, key):
                    return self
                async def execute(self):
                    # Mock rate limit: always 1 current count, positive TTL
                    return [1, 60]
            return MockPipeline(self)

        async def expire(self, key, time):
            return True

        async def ping(self):
            return True

    redis.redis_client = MockRedisClient()
    yield redis.redis_client

    # Restore old client
    redis.redis_client = old_client

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
