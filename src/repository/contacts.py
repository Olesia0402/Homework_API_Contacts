from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import Contact, User
from src.schemas.schemas import ContactCreate, ContactUpdate, ContactStatusUpdate


async def get_contacts(skip: int, limit: int, user: User, db: AsyncSession) -> List[Contact]:
    stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
    

async def get_contact(contact_id: int, user: User, db: AsyncSession) -> Contact:
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactCreate, user: User, db: AsyncSession) -> Contact:
    contact = Contact(user_id=user.id, **body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: AsyncSession) -> Contact | None:
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name=body.first_name,
        contact.last_name=body.last_name,
        contact.email=body.email,
        contact.phone=body.phone,
        contact.birthday=body.birthday,
        contact.other_information=body.other_information
        contact.done = body.done
        await db.commit()
    return contact


async def update_status_contact(contact_id: int, body: ContactStatusUpdate, user: User, db: AsyncSession) -> Contact | None:
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.done = body.done
        await db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: AsyncSession)  -> Contact | None:
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
