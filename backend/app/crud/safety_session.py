from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.safety_session import SafetySession
from app.schemas.safety_session import SafetySessionCreate, SafetySessionUpdate

def get_safety_session(db: Session, session_id: int, user_id: int) -> Optional[SafetySession]:
    return db.query(SafetySession).filter(
        SafetySession.id == session_id,
        SafetySession.user_id == user_id
    ).first()

def get_safety_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[SafetySession]:
    return db.query(SafetySession).filter(SafetySession.user_id == user_id).offset(skip).limit(limit).all()

def create_safety_session(db: Session, session: SafetySessionCreate, user_id: int) -> SafetySession:
    db_session = SafetySession(**session.model_dump(), user_id=user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_safety_session(db: Session, session_id: int, user_id: int, session: SafetySessionUpdate) -> Optional[SafetySession]:
    db_session = get_safety_session(db, session_id=session_id, user_id=user_id)
    if db_session:
        update_data = session.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_session, key, value)
        db.commit()
        db.refresh(db_session)
    return db_session

def cancel_safety_session(db: Session, session_id: int, user_id: int) -> Optional[SafetySession]:
    db_session = get_safety_session(db, session_id=session_id, user_id=user_id)
    if db_session:
        db_session.status = "cancelled"
        db_session.cancelled_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_session)
    return db_session

def complete_safety_session(db: Session, session_id: int, user_id: int) -> Optional[SafetySession]:
    db_session = get_safety_session(db, session_id=session_id, user_id=user_id)
    if db_session:
        db_session.status = "completed"
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_safety_session(db: Session, session_id: int, user_id: int) -> bool:
    db_session = get_safety_session(db, session_id=session_id, user_id=user_id)
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False
