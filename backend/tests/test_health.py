import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Healthy"}

def test_v1_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Healthy"}
