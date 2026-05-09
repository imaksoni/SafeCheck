import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from app.models.user import User

@pytest.fixture
def test_user(db_session):
    user = User(
        firebase_uid="test_uid_session",
        email="session@example.com",
        full_name="Session Tester",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def other_user(db_session):
    user = User(
        firebase_uid="other_uid_session",
        email="other_session@example.com",
        full_name="Other Session Tester",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def get_auth_headers():
    return {"Authorization": "Bearer fake_token"}

@patch("app.api.deps.auth.verify_id_token")
def test_create_safety_session(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}
    now_str = datetime.now(timezone.utc).isoformat()
    future_str = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    response = client.post(
        "/api/v1/sessions",
        headers=get_auth_headers(),
        json={
            "title": "Walking home",
            "destination": "Home",
            "start_at": now_str,
            "deadline_at": future_str
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Walking home"
    assert data["destination"] == "Home"
    assert data["status"] == "active"
    assert "id" in data
    assert data["user_id"] == test_user.id

@patch("app.api.deps.auth.verify_id_token")
def test_get_safety_sessions(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}
    now_str = datetime.now(timezone.utc).isoformat()
    future_str = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    client.post(
        "/api/v1/sessions",
        headers=get_auth_headers(),
        json={
            "title": "Walking home",
            "start_at": now_str,
            "deadline_at": future_str
        }
    )

    response = client.get(
        "/api/v1/sessions",
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Walking home"

@patch("app.api.deps.auth.verify_id_token")
def test_cancel_safety_session(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}
    now_str = datetime.now(timezone.utc).isoformat()
    future_str = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    create_response = client.post(
        "/api/v1/sessions",
        headers=get_auth_headers(),
        json={
            "title": "Walking home",
            "start_at": now_str,
            "deadline_at": future_str
        }
    )
    session_id = create_response.json()["id"]

    cancel_response = client.post(
        f"/api/v1/sessions/{session_id}/cancel",
        headers=get_auth_headers()
    )

    assert cancel_response.status_code == 200
    data = cancel_response.json()
    assert data["status"] == "cancelled"
    assert data["cancelled_at"] is not None

@patch("app.api.deps.auth.verify_id_token")
def test_complete_safety_session(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}
    now_str = datetime.now(timezone.utc).isoformat()
    future_str = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    create_response = client.post(
        "/api/v1/sessions",
        headers=get_auth_headers(),
        json={
            "title": "Walking home",
            "start_at": now_str,
            "deadline_at": future_str
        }
    )
    session_id = create_response.json()["id"]

    complete_response = client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=get_auth_headers()
    )

    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["status"] == "completed"

@patch("app.api.deps.auth.verify_id_token")
def test_cannot_access_others_session(mock_verify_id_token, test_user, other_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}
    now_str = datetime.now(timezone.utc).isoformat()
    future_str = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    create_response = client.post(
        "/api/v1/sessions",
        headers=get_auth_headers(),
        json={
            "title": "Walking home",
            "start_at": now_str,
            "deadline_at": future_str
        }
    )
    session_id = create_response.json()["id"]

    mock_verify_id_token.return_value = {"uid": other_user.firebase_uid}
    get_response = client.get(
        f"/api/v1/sessions/{session_id}",
        headers=get_auth_headers()
    )
    assert get_response.status_code == 404

@patch("app.api.deps.auth.verify_id_token")
@patch("app.api.v1.safety_sessions.cache_get")
@patch("app.api.v1.safety_sessions.cache_set")
def test_sessions_list_caching(mock_cache_set, mock_cache_get, mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Simulate a cache miss
    mock_cache_get.return_value = None

    response = client.get(
        "/api/v1/sessions",
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
    mock_cache_get.assert_called_once()
    mock_cache_set.assert_called_once()

    # Simulate a cache hit
    mock_cache_get.reset_mock()
    mock_cache_set.reset_mock()
    mock_cache_get.return_value = '[{"id": 999, "user_id": 1, "title": "Cached Session", "status": "active", "start_at": "2023-01-01T00:00:00Z", "deadline_at": "2023-01-01T01:00:00Z", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"}]'

    response = client.get(
        "/api/v1/sessions",
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Cached Session"

    mock_cache_get.assert_called_once()
    mock_cache_set.assert_not_called()

@patch("app.api.deps.auth.verify_id_token")
@patch("app.api.v1.safety_sessions.cache_get")
@patch("app.api.v1.safety_sessions.cache_set")
def test_read_session_caching(mock_cache_set, mock_cache_get, mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Setup: Create a completed session
    create_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": "Bearer fake_token"},
        json={
            "title": "Evening Run",
            "start_at": "2023-01-01T18:00:00Z",
            "deadline_at": "2023-01-01T19:00:00Z"
        }
    )
    session_id = create_response.json()["id"]
    client.post(f"/api/v1/sessions/{session_id}/complete", headers={"Authorization": "Bearer fake_token"})

    # Simulate a cache miss on the completed session
    mock_cache_get.return_value = None

    response = client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
    mock_cache_get.assert_called_once()
    mock_cache_set.assert_called_once()  # Should cache because it is safe (not active)

    # Setup: Create an active session
    create_response2 = client.post(
        "/api/v1/sessions",
        headers={"Authorization": "Bearer fake_token"},
        json={
            "title": "Morning Run",
            "start_at": "2023-01-01T08:00:00Z",
            "deadline_at": "2023-01-01T09:00:00Z"
        }
    )
    session_id2 = create_response2.json()["id"]

    mock_cache_get.reset_mock()
    mock_cache_set.reset_mock()
    mock_cache_get.return_value = None

    response2 = client.get(
        f"/api/v1/sessions/{session_id2}",
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response2.status_code == 200
    mock_cache_get.assert_called_once()
    mock_cache_set.assert_not_called()  # Should NOT cache because it is active
