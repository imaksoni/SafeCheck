from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class DeviceBase(BaseModel):
    platform: str
    device_name: str
    fcm_token: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    fcm_token: Optional[str] = None
    is_active: Optional[bool] = None

class DeviceHeartbeat(BaseModel):
    pass # No payload needed, just updating last_seen_at

class DeviceFCMToken(BaseModel):
    fcm_token: str

class DeviceResponse(DeviceBase):
    id: int
    user_id: int
    is_active: bool
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
