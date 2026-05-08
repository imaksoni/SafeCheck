from datetime import datetime
from datetime import timezone
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer

from app.db.session import Base

class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"))
    contact_id: Mapped[int] = mapped_column(ForeignKey("trusted_contacts.id"))

    # Statuses: pending, sent, failed
    status: Mapped[str] = mapped_column(String, default="pending")

    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    alert = relationship("Alert", back_populates="deliveries")
    contact = relationship("TrustedContact", backref="alert_deliveries")
