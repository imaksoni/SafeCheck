from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

class TrustedContact(Base):
    __tablename__ = "trusted_contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    relation: Mapped[Optional[str]] = mapped_column(String)
    allow_session_alerts: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_lost_phone_alerts: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="trusted_contacts")
