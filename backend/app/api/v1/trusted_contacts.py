from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trusted_contact import TrustedContactCreate, TrustedContactResponse, TrustedContactUpdate
from app.crud import trusted_contact as crud_trusted_contact
from app.core.redis_keys import get_cache_key_v1
from app.core.redis import cache_get, cache_set, cache_delete

router = APIRouter()

@router.get("/", response_model=List[TrustedContactResponse])
async def read_trusted_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve trusted contacts for the current user.
    """
    cache_key = get_cache_key_v1("trusted_contacts", str(current_user.id))
    cached_data = await cache_get(cache_key)
    if cached_data:
        return TypeAdapter(List[TrustedContactResponse]).validate_json(cached_data)

    contacts = await run_in_threadpool(
        crud_trusted_contact.get_trusted_contacts_by_user, db, user_id=current_user.id
    )

    ta = TypeAdapter(List[TrustedContactResponse])
    contacts_json = ta.dump_json(ta.validate_python(contacts)).decode()
    await cache_set(cache_key, contacts_json, 60)

    return contacts

@router.post("/", response_model=TrustedContactResponse, status_code=status.HTTP_201_CREATED)
async def create_trusted_contact(
    contact_in: TrustedContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new trusted contact.
    """
    contact = await run_in_threadpool(
        crud_trusted_contact.create_trusted_contact, db=db, contact=contact_in, user_id=current_user.id
    )
    await cache_delete(get_cache_key_v1("trusted_contacts", str(current_user.id)))
    return contact

@router.put("/{contact_id}", response_model=TrustedContactResponse)
async def update_trusted_contact(
    contact_id: int,
    contact_in: TrustedContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a trusted contact.
    """
    contact = await run_in_threadpool(
        crud_trusted_contact.get_trusted_contact, db=db, contact_id=contact_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Trusted contact not found")
    if contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    contact = await run_in_threadpool(
        crud_trusted_contact.update_trusted_contact, db=db, db_contact=contact, contact=contact_in
    )
    await cache_delete(get_cache_key_v1("trusted_contacts", str(current_user.id)))
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trusted_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a trusted contact.
    """
    contact = await run_in_threadpool(
        crud_trusted_contact.get_trusted_contact, db=db, contact_id=contact_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Trusted contact not found")
    if contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await run_in_threadpool(
        crud_trusted_contact.delete_trusted_contact, db=db, db_contact=contact
    )
    await cache_delete(get_cache_key_v1("trusted_contacts", str(current_user.id)))
