from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import safety_session as crud_session
from app.crud import snapshot as crud_snapshot
from app.schemas.safety_session import SafetySessionResponse, SafetySessionCreate, SafetySessionUpdate
from app.schemas.snapshot import SnapshotResponse
from app.models.user import User

router = APIRouter()

@router.post("", response_model=SafetySessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session: SafetySessionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return crud_session.create_safety_session(db=db, session=session, user_id=current_user.id)

@router.get("", response_model=List[SafetySessionResponse])
def read_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return crud_session.get_safety_sessions(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{session_id}", response_model=SafetySessionResponse)
def read_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = crud_session.get_safety_session(db, session_id=session_id, user_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")
    return db_session

@router.put("/{session_id}", response_model=SafetySessionResponse)
def update_session(
    session_id: int,
    session: SafetySessionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = crud_session.update_safety_session(db, session_id=session_id, user_id=current_user.id, session=session)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")
    return db_session

@router.post("/{session_id}/cancel", response_model=SafetySessionResponse)
def cancel_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = crud_session.cancel_safety_session(db, session_id=session_id, user_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")
    return db_session

@router.post("/{session_id}/complete", response_model=SafetySessionResponse)
def complete_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = crud_session.complete_safety_session(db, session_id=session_id, user_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")
    return db_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not crud_session.delete_safety_session(db, session_id=session_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Safety session not found")

@router.get("/{session_id}/snapshots", response_model=List[SnapshotResponse])
def get_session_snapshots(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = crud_session.get_safety_session(db, session_id=session_id, user_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")

    return crud_snapshot.get_session_snapshots(db, session_id=session_id, user_id=current_user.id, skip=skip, limit=limit)
