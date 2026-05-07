from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class TrustedContactBase(BaseModel):
    name: str
    phone: str
    relation: Optional[str] = None
    allow_session_alerts: bool = False
    allow_lost_phone_alerts: bool = False

class TrustedContactCreate(TrustedContactBase):
    pass

class TrustedContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    relation: Optional[str] = None
    allow_session_alerts: Optional[bool] = None
    allow_lost_phone_alerts: Optional[bool] = None

class TrustedContactResponse(TrustedContactBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
