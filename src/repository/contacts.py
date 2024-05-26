from typing import List

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.schemas import ContactCreate, ContactUpdate, ContactStatusUpdate


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()


async def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
    contact = Contact(user_id=user.id, **body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if contact:
        contact.first_name=body.first_name,
        contact.last_name=body.last_name,
        contact.email=body.email,
        contact.phone=body.phone,
        contact.birthday=body.birthday,
        contact.other_information=body.other_information
        contact.done = body.done
        db.commit()
    return contact


async def update_status_contact(contact_id: int, body: ContactStatusUpdate, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if contact:
        contact.done = body.done
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session)  -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact
