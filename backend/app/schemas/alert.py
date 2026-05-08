from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.schemas.snapshot import SnapshotCreate, SnapshotResponse


class AlertDeliveryBase(BaseModel):
    status: str
    retry_count: int
    next_retry_at: Optional[datetime] = None

class AlertDeliveryCreate(AlertDeliveryBase):
    alert_id: int
    contact_id: int

class AlertDeliveryResponse(AlertDeliveryBase):
    id: int
    alert_id: int
    contact_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertBase(BaseModel):
    type: str

class AlertCreate(AlertBase):
    user_id: int
    session_id: Optional[int] = None
    snapshot_id: Optional[int] = None

class AlertResponse(AlertBase):
    id: int
    user_id: int
    session_id: Optional[int] = None
    snapshot_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SOSCreate(BaseModel):
    session_id: Optional[int] = None
    snapshot: Optional[SnapshotCreate] = None


class LostPhoneAlertResponse(BaseModel):
    alert_id: int
    created_at: datetime
    type: str
    snapshot: Optional[SnapshotResponse] = None
    last_synced_at: Optional[datetime] = None
    notified_contacts: list[str]

    model_config = ConfigDict(from_attributes=True)
