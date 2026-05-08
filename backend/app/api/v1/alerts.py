from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import snapshot as crud_snapshot
from app.crud import alert as crud_alert
from app.crud import trusted_contact as crud_trusted_contact
from app.schemas.alert import AlertResponse, SOSCreate, AlertCreate
from app.schemas.snapshot import SnapshotCreate
from app.models.user import User

router = APIRouter()

@router.post("/sos", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    sos_data: SOSCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    snapshot_id = None

    # 1. Handle snapshot
    if sos_data.snapshot:
        # Create a new snapshot
        new_snapshot = crud_snapshot.create_snapshot(db=db, snapshot=sos_data.snapshot, user_id=current_user.id)
        snapshot_id = new_snapshot.id
    else:
        # Get latest stored snapshot
        latest_snapshot = crud_snapshot.get_latest_snapshot(db=db, user_id=current_user.id)
        if latest_snapshot:
            snapshot_id = latest_snapshot.id

    # 2. Create the Alert
    alert_create = AlertCreate(
        type="sos",
        user_id=current_user.id,
        session_id=sos_data.session_id,
        snapshot_id=snapshot_id
    )
    new_alert = crud_alert.create_alert(db=db, alert=alert_create)

    # 3. Create AlertDelivery records for trusted contacts
    contacts = crud_trusted_contact.get_trusted_contacts_by_user(db=db, user_id=current_user.id)
    for contact in contacts:
        if contact.allow_session_alerts:
            crud_alert.create_alert_delivery(db=db, alert_id=new_alert.id, contact_id=contact.id)

    return new_alert
