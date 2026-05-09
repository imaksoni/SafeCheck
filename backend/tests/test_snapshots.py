import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from app.models.user import User
from app.models.safety_session import SafetySession

@pytest.fixture
def test_user(db_session):
    user = User(
        firebase_uid="test_uid_snapshot",
        email="snapshot@example.com",
        full_name="Snapshot Tester",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_session(db_session, test_user):
    session = SafetySession(
        user_id=test_user.id,
        title="Walking home",
        start_at=datetime.now(timezone.utc),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=1),
        status="active"
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session

def get_auth_headers():
    return {"Authorization": "Bearer fake_token"}

@patch("app.api.deps.auth.verify_id_token")
def test_create_snapshot(mock_verify_id_token, test_user, test_session, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}
    now_str = datetime.now(timezone.utc).isoformat()

    response = client.post(
        "/api/v1/snapshots",
        headers=get_auth_headers(),
        json={
            "session_id": test_session.id,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 10.5,
            "battery_percent": 85,
            "is_battery_low": False,
            "network_type": "wifi",
            "is_online": True,
            "captured_at": now_str,
            "source": "manual"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["latitude"] == 40.7128
    assert data["battery_percent"] == 85
    assert data["session_id"] == test_session.id
    assert "id" in data
    assert data["user_id"] == test_user.id

@patch("app.api.deps.auth.verify_id_token")
def test_get_latest_snapshot(mock_verify_id_token, test_user, test_session, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Create two snapshots
    client.post(
        "/api/v1/snapshots",
        headers=get_auth_headers(),
        json={
            "session_id": test_session.id,
            "latitude": 40.0,
            "longitude": -74.0,
            "battery_percent": 80,
            "is_battery_low": False,
            "network_type": "wifi",
            "is_online": True,
            "captured_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
            "source": "background"
        }
    )

    client.post(
        "/api/v1/snapshots",
        headers=get_auth_headers(),
        json={
            "session_id": test_session.id,
            "latitude": 41.0,
            "longitude": -75.0,
            "battery_percent": 75,
            "is_battery_low": False,
            "network_type": "cellular",
            "is_online": True,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source": "background"
        }
    )

    response = client.get(
        "/api/v1/snapshots/latest",
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 41.0
    assert data["battery_percent"] == 75

@patch("app.api.deps.auth.verify_id_token")
def test_get_session_snapshots(mock_verify_id_token, test_user, test_session, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Create snapshot for session
    client.post(
        "/api/v1/snapshots",
        headers=get_auth_headers(),
        json={
            "session_id": test_session.id,
            "latitude": 40.0,
            "longitude": -74.0,
            "battery_percent": 80,
            "is_battery_low": False,
            "network_type": "wifi",
            "is_online": True,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source": "manual"
        }
    )

    response = client.get(
        f"/api/v1/sessions/{test_session.id}/snapshots",
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["latitude"] == 40.0

@patch("app.api.deps.auth.verify_id_token")
@patch("app.api.v1.snapshots.cache_get")
@patch("app.api.v1.snapshots.cache_set")
def test_get_latest_snapshot_caching(mock_cache_set, mock_cache_get, mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Setup: Create a snapshot first to avoid 404
    client.post(
        "/api/v1/snapshots",
        headers={"Authorization": "Bearer fake_token"},
        json={
            "latitude": 40.7128,
            "longitude": -74.0060,
            "battery_percent": 80,
            "is_battery_low": False,
            "network_type": "wifi",
            "is_online": True,
            "captured_at": "2023-01-01T12:00:00Z",
            "source": "background"
        }
    )

    # Simulate a cache miss
    mock_cache_get.return_value = None

    response = client.get(
        "/api/v1/snapshots/latest",
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
    mock_cache_get.assert_called_once()
    mock_cache_set.assert_called_once()

    # Simulate a cache hit
    mock_cache_get.reset_mock()
    mock_cache_set.reset_mock()
    mock_cache_get.return_value = '{"id": 999, "user_id": 1, "latitude": 10.0, "longitude": 20.0, "battery_percent": 100, "is_battery_low": false, "network_type": "wifi", "is_online": true, "captured_at": "2023-01-01T12:00:00Z", "received_at": "2023-01-01T12:00:00Z", "source": "test"}'

    response = client.get(
        "/api/v1/snapshots/latest",
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 999
    assert data["latitude"] == 10.0

    mock_cache_get.assert_called_once()
    mock_cache_set.assert_not_called()
