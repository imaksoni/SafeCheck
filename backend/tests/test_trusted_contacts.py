import pytest
from unittest.mock import patch
from app.models.user import User

@pytest.fixture
def test_user(db_session):
    user = User(
        firebase_uid="test_uid_trusted",
        email="test_trusted@example.com",
        full_name="Trusted Tester",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def other_user(db_session):
    user = User(
        firebase_uid="other_uid",
        email="other@example.com",
        full_name="Other Tester",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def get_auth_headers():
    return {"Authorization": "Bearer fake_token"}

@patch("app.api.deps.auth.verify_id_token")
def test_create_trusted_contact(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    response = client.post(
        "/api/v1/trusted-contacts/",
        headers=get_auth_headers(),
        json={
            "name": "Jane Doe",
            "phone": "+19876543210",
            "relation": "Sister",
            "allow_session_alerts": True,
            "allow_lost_phone_alerts": False
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["phone"] == "+19876543210"
    assert data["relation"] == "Sister"
    assert data["allow_session_alerts"] is True
    assert data["allow_lost_phone_alerts"] is False
    assert "id" in data
    assert data["user_id"] == test_user.id

@patch("app.api.deps.auth.verify_id_token")
def test_get_trusted_contacts(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Create contact
    client.post(
        "/api/v1/trusted-contacts/",
        headers=get_auth_headers(),
        json={
            "name": "Jane Doe",
            "phone": "+19876543210"
        }
    )

    response = client.get(
        "/api/v1/trusted-contacts/",
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Jane Doe"

@patch("app.api.deps.auth.verify_id_token")
def test_update_trusted_contact(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Create
    create_response = client.post(
        "/api/v1/trusted-contacts/",
        headers=get_auth_headers(),
        json={"name": "Jane", "phone": "123"}
    )
    contact_id = create_response.json()["id"]

    # Update
    update_response = client.put(
        f"/api/v1/trusted-contacts/{contact_id}",
        headers=get_auth_headers(),
        json={"name": "Jane Smith", "allow_session_alerts": True}
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Jane Smith"
    assert data["allow_session_alerts"] is True
    assert data["phone"] == "123"

@patch("app.api.deps.auth.verify_id_token")
def test_delete_trusted_contact(mock_verify_id_token, test_user, client):
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}

    # Create
    create_response = client.post(
        "/api/v1/trusted-contacts/",
        headers=get_auth_headers(),
        json={"name": "Jane", "phone": "123"}
    )
    contact_id = create_response.json()["id"]

    # Delete
    delete_response = client.delete(
        f"/api/v1/trusted-contacts/{contact_id}",
        headers=get_auth_headers()
    )
    assert delete_response.status_code == 204

    # Verify deletion
    get_response = client.get(
        "/api/v1/trusted-contacts/",
        headers=get_auth_headers()
    )
    assert len(get_response.json()) == 0

@patch("app.api.deps.auth.verify_id_token")
def test_cannot_access_others_contact(mock_verify_id_token, test_user, other_user, client):
    # Setup: test_user creates a contact
    mock_verify_id_token.return_value = {"uid": test_user.firebase_uid}
    create_response = client.post(
        "/api/v1/trusted-contacts/",
        headers=get_auth_headers(),
        json={"name": "Jane", "phone": "123"}
    )
    contact_id = create_response.json()["id"]

    # Action: other_user tries to update it
    mock_verify_id_token.return_value = {"uid": other_user.firebase_uid}
    update_response = client.put(
        f"/api/v1/trusted-contacts/{contact_id}",
        headers=get_auth_headers(),
        json={"name": "Hacked"}
    )
    assert update_response.status_code == 403

    # Action: other_user tries to delete it
    delete_response = client.delete(
        f"/api/v1/trusted-contacts/{contact_id}",
        headers=get_auth_headers()
    )
    assert delete_response.status_code == 403
