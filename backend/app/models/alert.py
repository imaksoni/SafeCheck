from datetime import datetime
from datetime import timezone
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer

from app.db.session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("safety_sessions.id"))
    snapshot_id: Mapped[Optional[int]] = mapped_column(ForeignKey("snapshots.id"))

    # Types: sos, timer_expired, lost_phone
    type: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="alerts")
    session = relationship("SafetySession", backref="alerts")
    snapshot = relationship("Snapshot", backref="alerts")
    deliveries = relationship("AlertDelivery", back_populates="alert", cascade="all, delete-orphan")
