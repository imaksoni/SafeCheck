from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class SafetySessionBase(BaseModel):
    title: str
    destination: Optional[str] = None
    companion_name: Optional[str] = None
    companion_phone: Optional[str] = None
    notes: Optional[str] = None
    status: str = "active"
    start_at: datetime
    deadline_at: datetime
    cancelled_at: Optional[datetime] = None
    alert_sent_at: Optional[datetime] = None

class SafetySessionCreate(SafetySessionBase):
    pass

class SafetySessionUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    companion_name: Optional[str] = None
    companion_phone: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    start_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    alert_sent_at: Optional[datetime] = None

class SafetySessionResponse(SafetySessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
