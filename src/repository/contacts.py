from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import Contact, User
from src.schemas.schemas import ContactCreate, ContactUpdate, ContactStatusUpdate


async def get_contacts(skip: int, limit: int, user: User, db: AsyncSession) -> List[Contact]:

    """
    The get_contacts function returns a list of contacts for the given user.

    :param skip: int: Skip a number of contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param user: User: Filter the contacts by user
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """

    stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
    

async def get_contact(contact_id: int, user: User, db: AsyncSession) -> Contact:
    
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param user: User: Ensure that the user is only able to access contacts they have created
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object, which is the contact with the given id
    :doc-author: Trelent
    """

    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactCreate, user: User, db: AsyncSession) -> Contact:
    
    """
    The create_contact function creates a new contact for the user.

    :param body: ContactCreate: Pass the request body to the function
    :param user: User: Get the user_id from the logged in user
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    
    contact = Contact(user_id=user.id, **body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: AsyncSession) -> Contact | None:
    
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactUpdate): A ContactUpdate object containing all fields that can be updated for a given user's contacts.

    :param contact_id: int: Specify the id of the contact to be updated
    :param body: ContactUpdate: Get the new values for the contact
    :param user: User: Make sure that the user is only able to update their own contacts
    :param db: AsyncSession: Create a database connection
    :return: The updated contact
    :doc-author: Trelent
    """

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
    
    """
    The update_status_contact function updates the status of a contact.

    :param contact_id: int: Identify the contact to update
    :param body: ContactStatusUpdate: Get the value of done from the request body
    :param user: User: Make sure that the user is authenticated and authorized to access this endpoint
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object if the contact is found, otherwise it returns none
    :doc-author: Trelent
    """
    
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.done = body.done
        await db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: AsyncSession)  -> Contact | None:
    
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be removed
    :param user: User: Identify the user that is making the request
    :param db: AsyncSession: Pass in the database session object
    :return: The contact that was removed
    :doc-author: Trelent
    """
    
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
