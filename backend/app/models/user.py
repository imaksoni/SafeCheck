from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    firebase_uid: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trusted_contacts = relationship("TrustedContact", back_populates="owner", cascade="all, delete-orphan")
