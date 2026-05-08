from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceHeartbeat, DeviceFCMToken
from app.crud import device as crud_device

router = APIRouter()

@router.post("/register", response_model=DeviceResponse)
def register_device(
    device_in: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a new device or return the existing one.
    """
    existing_device = crud_device.get_by_user_id_and_device_name(
        db=db, user_id=current_user.id, device_name=device_in.device_name
    )
    if existing_device:
        # Update FCM token if provided, and bump last_seen_at
        if device_in.fcm_token:
            crud_device.update_fcm_token(db, existing_device, device_in.fcm_token)
        return crud_device.update_heartbeat(db, existing_device)

    return crud_device.create(db=db, device=device_in, user_id=current_user.id)

@router.post("/heartbeat", response_model=DeviceResponse)
def device_heartbeat(
    device_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the last_seen_at timestamp for a device.
    """
    device = crud_device.get_by_user_id_and_device_name(
        db=db, user_id=current_user.id, device_name=device_name
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return crud_device.update_heartbeat(db=db, db_obj=device)

@router.post("/fcm-token", response_model=DeviceResponse)
def update_fcm_token(
    device_name: str,
    token_in: DeviceFCMToken,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the FCM token for a device.
    """
    device = crud_device.get_by_user_id_and_device_name(
        db=db, user_id=current_user.id, device_name=device_name
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return crud_device.update_fcm_token(db=db, db_obj=device, fcm_token=token_in.fcm_token)
