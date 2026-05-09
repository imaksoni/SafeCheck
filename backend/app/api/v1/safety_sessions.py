from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.api import deps
from app.crud import safety_session as crud_session
from app.crud import snapshot as crud_snapshot
from app.schemas.safety_session import SafetySessionResponse, SafetySessionCreate, SafetySessionUpdate
from app.schemas.snapshot import SnapshotResponse
from app.models.user import User
from app.core.redis_keys import get_cache_key_v1
from app.core.redis import cache_get, cache_set, cache_delete, cache_delete_pattern

router = APIRouter()

async def _invalidate_session_caches(user_id: int, session_id: int | None = None):
    """Helper to invalidate session-related caches."""
    await cache_delete_pattern(get_cache_key_v1("sessions:list", f"{user_id}:*"))
    if session_id is not None:
        await cache_delete(get_cache_key_v1("session", f"{user_id}:{session_id}"))

@router.post("", response_model=SafetySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session: SafetySessionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    new_session = await run_in_threadpool(
        crud_session.create_safety_session, db=db, session=session, user_id=current_user.id
    )
    await _invalidate_session_caches(current_user.id, new_session.id)
    return new_session

@router.get("", response_model=List[SafetySessionResponse])
async def read_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    cache_key = get_cache_key_v1("sessions:list", f"{current_user.id}:{skip}:{limit}")
    cached_data = await cache_get(cache_key)
    if cached_data:
        return TypeAdapter(List[SafetySessionResponse]).validate_json(cached_data)

    sessions = await run_in_threadpool(
        crud_session.get_safety_sessions, db, user_id=current_user.id, skip=skip, limit=limit
    )

    ta = TypeAdapter(List[SafetySessionResponse])
    sessions_json = ta.dump_json(ta.validate_python(sessions)).decode()
    await cache_set(cache_key, sessions_json, 60)

    return sessions

@router.get("/{session_id}", response_model=SafetySessionResponse)
async def read_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    cache_key = get_cache_key_v1("session", f"{current_user.id}:{session_id}")
    cached_data = await cache_get(cache_key)
    if cached_data:
        return TypeAdapter(SafetySessionResponse).validate_json(cached_data)

    db_session = await run_in_threadpool(
        crud_session.get_safety_session, db, session_id=session_id, user_id=current_user.id
    )
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")

    # Only cache if it is safe to cache (e.g., status is not active meaning it is immutable)
    if db_session.status != "active":
        ta = TypeAdapter(SafetySessionResponse)
        session_json = ta.dump_json(ta.validate_python(db_session)).decode()
        await cache_set(cache_key, session_json, 30)

    return db_session

@router.put("/{session_id}", response_model=SafetySessionResponse)
async def update_session(
    session_id: int,
    session: SafetySessionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = await run_in_threadpool(
        crud_session.update_safety_session, db, session_id=session_id, user_id=current_user.id, session=session
    )
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")
    await _invalidate_session_caches(current_user.id, session_id)
    return db_session

@router.post("/{session_id}/cancel", response_model=SafetySessionResponse)
async def cancel_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = await run_in_threadpool(
        crud_session.cancel_safety_session, db, session_id=session_id, user_id=current_user.id
    )
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")
    await _invalidate_session_caches(current_user.id, session_id)
    return db_session

@router.post("/{session_id}/complete", response_model=SafetySessionResponse)
async def complete_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = await run_in_threadpool(
        crud_session.complete_safety_session, db, session_id=session_id, user_id=current_user.id
    )
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")
    await _invalidate_session_caches(current_user.id, session_id)
    return db_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    deleted = await run_in_threadpool(
        crud_session.delete_safety_session, db, session_id=session_id, user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Safety session not found")
    await _invalidate_session_caches(current_user.id, session_id)

@router.get("/{session_id}/snapshots", response_model=List[SnapshotResponse])
async def get_session_snapshots(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_session = await run_in_threadpool(
        crud_session.get_safety_session, db, session_id=session_id, user_id=current_user.id
    )
    if db_session is None:
        raise HTTPException(status_code=404, detail="Safety session not found")

    return await run_in_threadpool(
        crud_snapshot.get_session_snapshots, db, session_id=session_id, user_id=current_user.id, skip=skip, limit=limit
    )
