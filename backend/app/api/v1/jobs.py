from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Any

from app.db.session import get_db
from app.models.safety_session import SafetySession
from app.models.snapshot import Snapshot
from app.models.trusted_contact import TrustedContact
from app.models.alert import Alert
from app.models.alert_delivery import AlertDelivery

router = APIRouter()

@router.post("/process-expired-sessions", status_code=status.HTTP_200_OK)
def process_expired_sessions(db: Session = Depends(get_db)) -> Any:
    """
    Check for expired safety sessions and create alerts + deliveries.
    """
    now = datetime.utcnow()

    # Find active sessions that have passed their deadline and are not cancelled
    expired_sessions = db.query(SafetySession).filter(
        SafetySession.status == "active",
        SafetySession.cancelled_at.is_(None),
        SafetySession.deadline_at <= now,
        SafetySession.alert_sent_at.is_(None)
    ).all()

    processed_count = 0
    for session in expired_sessions:
        # Mark session as expired and set alert_sent_at
        session.status = "expired"
        session.alert_sent_at = now

        # Get latest snapshot for this user/session
        latest_snapshot = db.query(Snapshot).filter(
            Snapshot.user_id == session.user_id
        ).order_by(Snapshot.captured_at.desc()).first()

        snapshot_id = latest_snapshot.id if latest_snapshot else None

        # Create Alert
        new_alert = Alert(
            user_id=session.user_id,
            session_id=session.id,
            snapshot_id=snapshot_id,
            type="timer_expired",
            created_at=now
        )
        db.add(new_alert)
        db.flush() # flush to get new_alert.id

        # Find eligible trusted contacts
        contacts = db.query(TrustedContact).filter(
            TrustedContact.user_id == session.user_id,
            TrustedContact.allow_session_alerts == True
        ).all()

        # Create AlertDelivery for each contact
        for contact in contacts:
            delivery = AlertDelivery(
                alert_id=new_alert.id,
                contact_id=contact.id,
                status="pending",
                retry_count=0,
                created_at=now,
                updated_at=now
            )
            db.add(delivery)

        processed_count += 1

    db.commit()

    return {"message": f"Processed {processed_count} expired sessions."}
