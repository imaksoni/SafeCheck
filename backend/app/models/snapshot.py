from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Float, Boolean, Integer

from app.db.session import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("safety_sessions.id"))

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    accuracy: Mapped[Optional[float]] = mapped_column(Float)

    battery_percent: Mapped[int] = mapped_column(Integer)
    is_battery_low: Mapped[bool] = mapped_column(Boolean)

    network_type: Mapped[str] = mapped_column(String)
    is_online: Mapped[bool] = mapped_column(Boolean)

    captured_at: Mapped[datetime] = mapped_column(DateTime)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String)

    user = relationship("User", backref="snapshots")
    session = relationship("SafetySession", backref="snapshots")
