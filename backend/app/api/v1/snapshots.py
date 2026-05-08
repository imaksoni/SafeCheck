from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import snapshot as crud_snapshot
from app.schemas.snapshot import SnapshotCreate, SnapshotResponse
from app.models.user import User

router = APIRouter()

@router.post("", response_model=SnapshotResponse, status_code=status.HTTP_201_CREATED)
def create_snapshot(
    snapshot: SnapshotCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return crud_snapshot.create_snapshot(db=db, snapshot=snapshot, user_id=current_user.id)

@router.get("/latest", response_model=SnapshotResponse)
def get_latest_snapshot(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    snapshot = crud_snapshot.get_latest_snapshot(db=db, user_id=current_user.id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No snapshots found")
    return snapshot
