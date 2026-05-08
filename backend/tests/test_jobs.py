import pytest
from datetime import datetime, timezone, timedelta
from app.models.user import User
from app.models.safety_session import SafetySession
from app.models.snapshot import Snapshot
from app.models.trusted_contact import TrustedContact
from app.models.alert import Alert
from app.models.alert_delivery import AlertDelivery

def test_process_expired_sessions(client, db_session):
    # Setup Data
    user = User(
        firebase_uid="jobs_test_uid",
        email="jobtest@example.com",
        full_name="Job Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Contact that allows session alerts
    contact_allow = TrustedContact(
        user_id=user.id,
        name="Allow Alerts",
        phone="+1234567890",
        allow_session_alerts=True
    )
    # 2. Contact that does not allow session alerts
    contact_deny = TrustedContact(
        user_id=user.id,
        name="Deny Alerts",
        phone="+0987654321",
        allow_session_alerts=False
    )
    db_session.add(contact_allow)
    db_session.add(contact_deny)
    db_session.commit()
    db_session.refresh(contact_allow)

    # 3. Snapshot for the user
    snapshot = Snapshot(
        user_id=user.id,
        latitude=37.7749,
        longitude=-122.4194,
        battery_percent=80,
        is_battery_low=False,
        network_type="wifi",
        is_online=True,
        captured_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        source="background"
    )
    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)

    # 4. Expired safety session
    expired_session = SafetySession(
        user_id=user.id,
        title="Expired Walk",
        status="active",
        start_at=datetime.now(timezone.utc) - timedelta(hours=2),
        deadline_at=datetime.now(timezone.utc) - timedelta(minutes=10) # 10 mins ago
    )

    # 5. Future safety session (not expired)
    future_session = SafetySession(
        user_id=user.id,
        title="Future Walk",
        status="active",
        start_at=datetime.now(timezone.utc),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db_session.add(expired_session)
    db_session.add(future_session)
    db_session.commit()
    db_session.refresh(expired_session)
    db_session.refresh(future_session)

    # Call the endpoint
    response = client.post("/api/v1/jobs/process-expired-sessions")
    assert response.status_code == 200
    assert response.json()["message"] == "Processed 1 expired sessions."

    # Verify Database State

    # Session status and alert_sent_at
    db_session.refresh(expired_session)
    assert expired_session.status == "expired"
    assert expired_session.alert_sent_at is not None

    db_session.refresh(future_session)
    assert future_session.status == "active"
    assert future_session.alert_sent_at is None

    # Alert generation
    alert = db_session.query(Alert).filter(Alert.session_id == expired_session.id).first()
    assert alert is not None
    assert alert.type == "timer_expired"
    assert alert.snapshot_id == snapshot.id
    assert alert.user_id == user.id

    # Alert Deliveries
    deliveries = db_session.query(AlertDelivery).filter(AlertDelivery.alert_id == alert.id).all()
    assert len(deliveries) == 1 # Only the one allowing session alerts
    assert deliveries[0].contact_id == contact_allow.id
    assert deliveries[0].status == "pending"
    assert deliveries[0].retry_count == 0
