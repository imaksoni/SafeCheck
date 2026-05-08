import pytest
from unittest.mock import patch
from datetime import datetime, timedelta

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
    now_str = datetime.utcnow().isoformat()
    future_str = (datetime.utcnow() + timedelta(hours=1)).isoformat()

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
    now_str = datetime.utcnow().isoformat()
    future_str = (datetime.utcnow() + timedelta(hours=1)).isoformat()

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
    now_str = datetime.utcnow().isoformat()
    future_str = (datetime.utcnow() + timedelta(hours=1)).isoformat()

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
    now_str = datetime.utcnow().isoformat()
    future_str = (datetime.utcnow() + timedelta(hours=1)).isoformat()

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
    now_str = datetime.utcnow().isoformat()
    future_str = (datetime.utcnow() + timedelta(hours=1)).isoformat()

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
