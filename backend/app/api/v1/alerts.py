from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.api import deps
from app.core.idempotency import IdempotencyManager, IdempotencyConflictException
from app.crud import snapshot as crud_snapshot
from app.crud import alert as crud_alert
from app.crud import trusted_contact as crud_trusted_contact
from app.schemas.alert import AlertResponse, SOSCreate, AlertCreate, LostPhoneAlertResponse
from app.schemas.snapshot import SnapshotCreate, SnapshotResponse
from app.models.user import User
from app.core.config import settings
from app.core.rate_limit import UserRateLimiter

router = APIRouter()

def _sync_trigger_sos(db: Session, sos_data: SOSCreate, current_user: User) -> AlertResponse:
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

    return AlertResponse.model_validate(new_alert)


@router.post(
    "/sos",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(UserRateLimiter("sos", settings.RATE_LIMIT_SOS_ATTEMPTS, settings.RATE_LIMIT_SOS_WINDOW))
    ]
)
async def trigger_sos(
    sos_data: SOSCreate,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    idem_manager = IdempotencyManager("sos")

    if x_idempotency_key:
        try:
            cached_response = await idem_manager.check_and_lock(x_idempotency_key, current_user.id, sos_data)
            if cached_response is not None:
                return cached_response
        except IdempotencyConflictException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)

    try:
        response = await run_in_threadpool(_sync_trigger_sos, db, sos_data, current_user)

        if x_idempotency_key:
            await idem_manager.save_success(x_idempotency_key, current_user.id, sos_data, response)

        return response
    except Exception as e:
        if x_idempotency_key:
            await idem_manager.unlock(x_idempotency_key, current_user.id)
        raise e


def _sync_trigger_lost_phone(db: Session, current_user: User) -> LostPhoneAlertResponse:
    # 1. Get latest stored snapshot
    latest_snapshot = crud_snapshot.get_latest_snapshot(db=db, user_id=current_user.id)
    snapshot_id = latest_snapshot.id if latest_snapshot else None

    last_synced_at = None
    if latest_snapshot:
        last_synced_at = latest_snapshot.received_at or latest_snapshot.captured_at

    # 2. Create the Alert
    alert_create = AlertCreate(
        type="lost_phone",
        user_id=current_user.id,
        session_id=None,
        snapshot_id=snapshot_id
    )
    new_alert = crud_alert.create_alert(db=db, alert=alert_create)

    # 3. Create AlertDelivery records for trusted contacts
    contacts = crud_trusted_contact.get_trusted_contacts_by_user(db=db, user_id=current_user.id)
    notified_contacts = []
    for contact in contacts:
        if contact.allow_lost_phone_alerts:
            crud_alert.create_alert_delivery(db=db, alert_id=new_alert.id, contact_id=contact.id)
            notified_contacts.append(contact.name)

    return LostPhoneAlertResponse(
        alert_id=new_alert.id,
        created_at=new_alert.created_at,
        type=new_alert.type,
        snapshot=SnapshotResponse.model_validate(latest_snapshot) if latest_snapshot else None,
        last_synced_at=last_synced_at,
        notified_contacts=notified_contacts
    )


@router.post(
    "/lost-phone",
    response_model=LostPhoneAlertResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(UserRateLimiter("lost_phone", settings.RATE_LIMIT_LOST_PHONE_ATTEMPTS, settings.RATE_LIMIT_LOST_PHONE_WINDOW))
    ]
)
async def trigger_lost_phone(
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    idem_manager = IdempotencyManager("lost_phone")

    if x_idempotency_key:
        try:
            # We use an empty dict as payload since there is no body payload for this endpoint
            cached_response = await idem_manager.check_and_lock(x_idempotency_key, current_user.id, {})
            if cached_response is not None:
                return cached_response
        except IdempotencyConflictException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)

    try:
        response = await run_in_threadpool(_sync_trigger_lost_phone, db, current_user)

        if x_idempotency_key:
            await idem_manager.save_success(x_idempotency_key, current_user.id, {}, response)

        return response
    except Exception as e:
        if x_idempotency_key:
            await idem_manager.unlock(x_idempotency_key, current_user.id)
        raise e
