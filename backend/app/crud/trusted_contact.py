from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.trusted_contact import TrustedContact
from app.schemas.trusted_contact import TrustedContactCreate, TrustedContactUpdate

def get_trusted_contact(db: Session, contact_id: int) -> Optional[TrustedContact]:
    return db.query(TrustedContact).filter(TrustedContact.id == contact_id).first()

def get_trusted_contacts_by_user(db: Session, user_id: int) -> List[TrustedContact]:
    return db.query(TrustedContact).filter(TrustedContact.user_id == user_id).all()

def create_trusted_contact(db: Session, contact: TrustedContactCreate, user_id: int) -> TrustedContact:
    db_contact = TrustedContact(
        user_id=user_id,
        name=contact.name,
        phone=contact.phone,
        relation=contact.relation,
        allow_session_alerts=contact.allow_session_alerts,
        allow_lost_phone_alerts=contact.allow_lost_phone_alerts,
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_trusted_contact(db: Session, db_contact: TrustedContact, contact: TrustedContactUpdate) -> TrustedContact:
    update_data = contact.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_trusted_contact(db: Session, db_contact: TrustedContact) -> None:
    db.delete(db_contact)
    db.commit()
