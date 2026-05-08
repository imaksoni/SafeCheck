import pytest
from httpx import AsyncClient

# Since devices tests require auth and a DB session, we will mock or use the app client
# that is available via conftest (which usually sets up auth overrides).

def test_register_device(client):
    response = client.post(
        "/api/v1/devices/register",
        headers={"Authorization": "Bearer test-token"},
        json={
            "platform": "ios",
            "device_name": "iPhone 13",
            "fcm_token": "dummy_token"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "ios"
    assert data["device_name"] == "iPhone 13"
    assert data["fcm_token"] == "dummy_token"
    assert data["is_active"] is True
    assert "last_seen_at" in data

def test_register_existing_device(client):
    # Register once
    client.post(
        "/api/v1/devices/register",
        headers={"Authorization": "Bearer test-token"},
        json={
            "platform": "android",
            "device_name": "Pixel 6",
            "fcm_token": "token1"
        }
    )

    # Register again with new token
    response = client.post(
        "/api/v1/devices/register",
        headers={"Authorization": "Bearer test-token"},
        json={
            "platform": "android",
            "device_name": "Pixel 6",
            "fcm_token": "token2"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["fcm_token"] == "token2"

def test_heartbeat(client):
    client.post(
        "/api/v1/devices/register",
        headers={"Authorization": "Bearer test-token"},
        json={
            "platform": "android",
            "device_name": "Pixel 6",
            "fcm_token": "token1"
        }
    )

    response = client.post(
        "/api/v1/devices/heartbeat?device_name=Pixel 6",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True

def test_heartbeat_not_found(client):
    response = client.post(
        "/api/v1/devices/heartbeat?device_name=Unknown Device",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 404

def test_update_fcm_token(client):
    client.post(
        "/api/v1/devices/register",
        headers={"Authorization": "Bearer test-token"},
        json={
            "platform": "android",
            "device_name": "Pixel 6",
            "fcm_token": "token1"
        }
    )

    response = client.post(
        "/api/v1/devices/fcm-token?device_name=Pixel 6",
        headers={"Authorization": "Bearer test-token"},
        json={"fcm_token": "new_token_3"}
    )
    assert response.status_code == 200
    assert response.json()["fcm_token"] == "new_token_3"
