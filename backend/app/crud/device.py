from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate

def get(db: Session, device_id: int) -> Optional[Device]:
    return db.query(Device).filter(Device.id == device_id).first()

def get_by_user_id(db: Session, user_id: int) -> List[Device]:
    return db.query(Device).filter(Device.user_id == user_id).all()

def get_by_user_id_and_device_name(db: Session, user_id: int, device_name: str) -> Optional[Device]:
    return db.query(Device).filter(
        Device.user_id == user_id,
        Device.device_name == device_name
    ).first()

def create(db: Session, device: DeviceCreate, user_id: int) -> Device:
    db_obj = Device(
        user_id=user_id,
        platform=device.platform,
        device_name=device.device_name,
        fcm_token=device.fcm_token,
        is_active=True,
        last_seen_at=datetime.now(timezone.utc)
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Device, obj_in: DeviceUpdate) -> Device:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_heartbeat(db: Session, db_obj: Device) -> Device:
    db_obj.last_seen_at = datetime.now(timezone.utc)
    db_obj.is_active = True # Reactivate if it was inactive
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_fcm_token(db: Session, db_obj: Device, fcm_token: str) -> Device:
    db_obj.fcm_token = fcm_token
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
