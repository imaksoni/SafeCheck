from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.snapshot import Snapshot
from app.schemas.snapshot import SnapshotCreate

def create_snapshot(db: Session, snapshot: SnapshotCreate, user_id: int) -> Snapshot:
    db_snapshot = Snapshot(
        **snapshot.model_dump(),
        user_id=user_id,
        received_at=datetime.now(timezone.utc)
    )
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)
    return db_snapshot

def get_latest_snapshot(db: Session, user_id: int) -> Optional[Snapshot]:
    return db.query(Snapshot).filter(
        Snapshot.user_id == user_id
    ).order_by(Snapshot.captured_at.desc()).first()

def get_session_snapshots(db: Session, session_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Snapshot]:
    return db.query(Snapshot).filter(
        Snapshot.session_id == session_id,
        Snapshot.user_id == user_id
    ).order_by(Snapshot.captured_at.desc()).offset(skip).limit(limit).all()
