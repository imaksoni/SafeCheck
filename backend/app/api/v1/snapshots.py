from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.api import deps
from app.crud import snapshot as crud_snapshot
from app.schemas.snapshot import SnapshotCreate, SnapshotResponse
from app.models.user import User
from app.core.config import settings
from app.core.rate_limit import UserRateLimiter
from app.core.redis_keys import get_cache_key_v1
from app.core.redis import cache_get, cache_set, cache_delete

router = APIRouter()

@router.post(
    "",
    response_model=SnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(UserRateLimiter("snapshot", settings.RATE_LIMIT_SNAPSHOT_ATTEMPTS, settings.RATE_LIMIT_SNAPSHOT_WINDOW))]
)
async def create_snapshot(
    snapshot: SnapshotCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    snapshot_data = await run_in_threadpool(
        crud_snapshot.create_snapshot, db=db, snapshot=snapshot, user_id=current_user.id
    )
    await cache_delete(get_cache_key_v1("snapshots:latest", str(current_user.id)))
    return snapshot_data

@router.get("/latest", response_model=SnapshotResponse)
async def get_latest_snapshot(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieve the latest snapshot for the current user.
    Note: Data may be cached for a short duration and not strictly live.
    """
    cache_key = get_cache_key_v1("snapshots:latest", str(current_user.id))
    cached_data = await cache_get(cache_key)
    if cached_data:
        return TypeAdapter(SnapshotResponse).validate_json(cached_data)

    snapshot = await run_in_threadpool(
        crud_snapshot.get_latest_snapshot, db=db, user_id=current_user.id
    )
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No snapshots found")

    ta = TypeAdapter(SnapshotResponse)
    snapshot_json = ta.dump_json(ta.validate_python(snapshot)).decode()
    await cache_set(cache_key, snapshot_json, 30)

    return snapshot
