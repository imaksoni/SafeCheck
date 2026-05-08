import pytest
from unittest.mock import patch

@patch("app.api.v1.auth.auth.verify_id_token")
def test_firebase_login_success(mock_verify_id_token, client):
    # Mock the return value of verify_id_token
    mock_verify_id_token.return_value = {
        "uid": "test_firebase_uid_123",
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "name": "Test User",
    }

    response = client.post(
        "/api/v1/auth/firebase-login",
        json={"token": "valid_mock_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["firebase_uid"] == "test_firebase_uid_123"
    assert data["email"] == "test@example.com"
    assert data["phone"] == "+1234567890"
    assert data["full_name"] == "Test User"
    assert "id" in data

@patch("app.api.v1.auth.auth.verify_id_token")
def test_firebase_login_invalid_token(mock_verify_id_token, client):
    # Mock verify_id_token to throw an exception
    mock_verify_id_token.side_effect = Exception("Invalid token")

    response = client.post(
        "/api/v1/auth/firebase-login",
        json={"token": "invalid_token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Firebase ID token"

@patch("app.api.v1.auth.auth.verify_id_token")
def test_firebase_login_missing_uid(mock_verify_id_token, client):
    # Mock verify_id_token returning dict without uid
    mock_verify_id_token.return_value = {
        "email": "test@example.com",
    }

    response = client.post(
        "/api/v1/auth/firebase-login",
        json={"token": "valid_token_but_missing_uid"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token payload"
