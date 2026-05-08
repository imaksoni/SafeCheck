from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class SnapshotBase(BaseModel):
    session_id: Optional[int] = None
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    battery_percent: int
    is_battery_low: bool
    network_type: str
    is_online: bool
    captured_at: datetime
    source: str

class SnapshotCreate(SnapshotBase):
    pass

class SnapshotResponse(SnapshotBase):
    id: int
    user_id: int
    received_at: datetime

    model_config = ConfigDict(from_attributes=True)
