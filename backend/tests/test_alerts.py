from datetime import timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.trusted_contact import TrustedContact
from app.models.alert import Alert
from app.models.alert_delivery import AlertDelivery
from app.models.snapshot import Snapshot
import datetime
from unittest.mock import patch

def test_sos_with_provided_snapshot(client: TestClient, db_session: Session):
    with patch("app.api.deps.auth.verify_id_token") as mock_verify_id_token:
        mock_verify_id_token.return_value = {
            "uid": "test_firebase_uid_123",
            "email": "sos@example.com",
        }

        # Login to create user
        client.post("/api/v1/auth/firebase-login", json={"token": "valid_mock_token"})

        headers = {"Authorization": f"Bearer valid_mock_token"}

        # Get user id from DB
        from app.models.user import User
        user = db_session.query(User).filter(User.firebase_uid == "test_firebase_uid_123").first()
        user_id = user.id

        # Add a trusted contact with session alerts enabled
        client.post("/api/v1/trusted-contacts", headers=headers, json={
            "name": "Trusted Contact 1",
            "phone": "555-1234",
            "relation": "Friend",
            "allow_session_alerts": True,
            "allow_lost_phone_alerts": False
        })

        # Add a trusted contact with session alerts disabled
        client.post("/api/v1/trusted-contacts", headers=headers, json={
            "name": "Trusted Contact 2",
            "phone": "555-5678",
            "allow_session_alerts": False,
            "allow_lost_phone_alerts": False
        })

        sos_payload = {
            "session_id": None,
            "snapshot": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "accuracy": 10.0,
                "battery_percent": 80,
                "is_battery_low": False,
                "network_type": "wifi",
                "is_online": True,
                "captured_at": datetime.datetime.now(timezone.utc).isoformat(),
                "source": "manual_sos"
            }
        }

        response = client.post("/api/v1/alerts/sos", json=sos_payload, headers=headers)
        assert response.status_code == 201
        alert_data = response.json()
        assert alert_data["type"] == "sos"
        assert alert_data["user_id"] == user_id
        assert alert_data["snapshot_id"] is not None

        alert_id = alert_data["id"]
        snapshot_id = alert_data["snapshot_id"]

        # Verify snapshot in DB
        db_snapshot = db_session.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
        assert db_snapshot is not None
        assert db_snapshot.latitude == 37.7749

        # Verify alert in DB
        db_alert = db_session.query(Alert).filter(Alert.id == alert_id).first()
        assert db_alert is not None
        assert db_alert.type == "sos"

        # Verify delivery records in DB
        deliveries = db_session.query(AlertDelivery).filter(AlertDelivery.alert_id == alert_id).all()
        assert len(deliveries) == 1

        contact = db_session.query(TrustedContact).filter(TrustedContact.id == deliveries[0].contact_id).first()
        assert contact.name == "Trusted Contact 1"


def test_sos_without_provided_snapshot(client: TestClient, db_session: Session):
    with patch("app.api.deps.auth.verify_id_token") as mock_verify_id_token:
        mock_verify_id_token.return_value = {
            "uid": "test_firebase_uid_1234",
            "email": "sos2@example.com",
        }

        # Login to create user
        client.post("/api/v1/auth/firebase-login", json={"token": "valid_mock_token_2"})

        headers = {"Authorization": f"Bearer valid_mock_token_2"}

        # Get user id
        from app.models.user import User
        user = db_session.query(User).filter(User.firebase_uid == "test_firebase_uid_1234").first()
        user_id = user.id

        # Add a prior snapshot manually via endpoint
        snap_payload = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 15.0,
            "battery_percent": 50,
            "is_battery_low": False,
            "network_type": "cellular",
            "is_online": True,
            "captured_at": datetime.datetime.now(timezone.utc).isoformat(),
            "source": "background"
        }
        client.post("/api/v1/snapshots", json=snap_payload, headers=headers)

        # Call SOS without snapshot
        sos_payload = {
            "session_id": None,
            "snapshot": None
        }

        response = client.post("/api/v1/alerts/sos", json=sos_payload, headers=headers)
        assert response.status_code == 201
        alert_data = response.json()
        assert alert_data["type"] == "sos"
        assert alert_data["user_id"] == user_id
        assert alert_data["snapshot_id"] is not None

        alert_id = alert_data["id"]
        snapshot_id = alert_data["snapshot_id"]

        # Verify the snapshot linked is the one we created
        db_snapshot = db_session.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
        assert db_snapshot is not None
        assert db_snapshot.latitude == 40.7128

def test_lost_phone_with_snapshot(client: TestClient, db_session: Session):
    with patch("app.api.deps.auth.verify_id_token") as mock_verify_id_token:
        mock_verify_id_token.return_value = {
            "uid": "test_firebase_uid_lost1",
            "email": "lost1@example.com",
        }

        # Login to create user
        client.post("/api/v1/auth/firebase-login", json={"token": "valid_mock_token_lost1"})

        headers = {"Authorization": f"Bearer valid_mock_token_lost1"}

        # Add a prior snapshot manually via endpoint
        snap_payload = {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "accuracy": 15.0,
            "battery_percent": 50,
            "is_battery_low": False,
            "network_type": "cellular",
            "is_online": True,
            "captured_at": datetime.datetime.now(timezone.utc).isoformat(),
            "source": "background"
        }
        client.post("/api/v1/snapshots", json=snap_payload, headers=headers)

        # Add a trusted contact with lost_phone alerts enabled
        client.post("/api/v1/trusted-contacts", headers=headers, json={
            "name": "Lost Contact 1",
            "phone": "555-1111",
            "relation": "Family",
            "allow_session_alerts": False,
            "allow_lost_phone_alerts": True
        })

        # Add a trusted contact with lost_phone alerts disabled
        client.post("/api/v1/trusted-contacts", headers=headers, json={
            "name": "Lost Contact 2",
            "phone": "555-2222",
            "allow_session_alerts": False,
            "allow_lost_phone_alerts": False
        })

        # Trigger lost phone alert
        response = client.post("/api/v1/alerts/lost-phone", headers=headers)
        assert response.status_code == 201
        alert_data = response.json()

        assert alert_data["type"] == "lost_phone"
        assert alert_data["snapshot"] is not None
        assert alert_data["snapshot"]["latitude"] == 34.0522
        assert alert_data["last_synced_at"] is not None
        assert "Lost Contact 1" in alert_data["notified_contacts"]
        assert "Lost Contact 2" not in alert_data["notified_contacts"]

def test_lost_phone_without_snapshot(client: TestClient, db_session: Session):
    with patch("app.api.deps.auth.verify_id_token") as mock_verify_id_token:
        mock_verify_id_token.return_value = {
            "uid": "test_firebase_uid_lost2",
            "email": "lost2@example.com",
        }

        # Login to create user
        client.post("/api/v1/auth/firebase-login", json={"token": "valid_mock_token_lost2"})

        headers = {"Authorization": f"Bearer valid_mock_token_lost2"}

        # No snapshot added here

        # Trigger lost phone alert
        response = client.post("/api/v1/alerts/lost-phone", headers=headers)
        assert response.status_code == 201
        alert_data = response.json()

        assert alert_data["type"] == "lost_phone"
        assert alert_data["snapshot"] is None
        assert alert_data["last_synced_at"] is None
        assert alert_data["notified_contacts"] == []
