import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

from app.core import redis

def test_root_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    expected_redis = "unconfigured" if redis.redis_client is None else "ok"
    assert response.json() == {"status": "ok", "message": "Healthy", "redis": expected_redis}

def test_v1_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    expected_redis = "unconfigured" if redis.redis_client is None else "ok"
    assert response.json() == {"status": "ok", "message": "Healthy", "redis": expected_redis}
