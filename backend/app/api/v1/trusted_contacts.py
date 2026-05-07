from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trusted_contact import TrustedContactCreate, TrustedContactResponse, TrustedContactUpdate
from app.crud import trusted_contact as crud_trusted_contact

router = APIRouter()

@router.get("/", response_model=List[TrustedContactResponse])
def read_trusted_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve trusted contacts for the current user.
    """
    contacts = crud_trusted_contact.get_trusted_contacts_by_user(db, user_id=current_user.id)
    return contacts

@router.post("/", response_model=TrustedContactResponse, status_code=status.HTTP_201_CREATED)
def create_trusted_contact(
    contact_in: TrustedContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new trusted contact.
    """
    contact = crud_trusted_contact.create_trusted_contact(db=db, contact=contact_in, user_id=current_user.id)
    return contact

@router.put("/{contact_id}", response_model=TrustedContactResponse)
def update_trusted_contact(
    contact_id: int,
    contact_in: TrustedContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a trusted contact.
    """
    contact = crud_trusted_contact.get_trusted_contact(db=db, contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Trusted contact not found")
    if contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    contact = crud_trusted_contact.update_trusted_contact(db=db, db_contact=contact, contact=contact_in)
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trusted_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a trusted contact.
    """
    contact = crud_trusted_contact.get_trusted_contact(db=db, contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Trusted contact not found")
    if contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud_trusted_contact.delete_trusted_contact(db=db, db_contact=contact)
