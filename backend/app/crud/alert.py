from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.alert_delivery import AlertDelivery
from app.schemas.alert import AlertCreate

def create_alert(db: Session, alert: AlertCreate) -> Alert:
    db_alert = Alert(
        user_id=alert.user_id,
        session_id=alert.session_id,
        snapshot_id=alert.snapshot_id,
        type=alert.type,
        created_at=datetime.utcnow()
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def create_alert_delivery(db: Session, alert_id: int, contact_id: int) -> AlertDelivery:
    db_delivery = AlertDelivery(
        alert_id=alert_id,
        contact_id=contact_id,
        status="pending",
        retry_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery
