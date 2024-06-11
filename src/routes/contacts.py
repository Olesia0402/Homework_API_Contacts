from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, extract

from src.database.db import get_db
from src.database.models import User
from src.schemas.schemas import ContactCreate, ContactResponse, ContactStatusUpdate, ContactUpdate
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


class SomeDuplicateEmailException(Exception):
    pass


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The read_contacts function returns a list of contacts.

    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The read_contact function is used to retrieve a single contact from the database.
    It takes in an integer representing the id of the contact and returns a Contact object.

    :param contact_id: int: Specify the contact to be updated
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 2 contact per 5 minutes',
            dependencies=[Depends(RateLimiter(times=2, seconds=300))])
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The create_contact function creates a new contact in the database.
        It takes an object of type ContactCreate as input and returns an object of type Contact.
        The user must be logged in to create a contact.

    :param body: ContactCreate: Define the type of data that is expected to be passed in
    :param db: AsyncSession: Pass the database session to the repository layer
    :param current_user: User: Get the user that is currently logged in
    :return: A contact object
    :doc-author: Trelent
    """
    
    try:
        return await repository_contacts.create_contact(body, current_user, db)
    except SomeDuplicateEmailException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or number value is not unique")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The update_contact function updates a contact in the database.
        It takes an id of the contact to update, and a body containing the fields to update.
        The function returns an updated Contact object.

    :param body: ContactUpdate: Get the data from the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_status_contact(body: ContactStatusUpdate, contact_id: int, db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The update_status_contact function updates the status of a contact.
        The function takes in an id, body and db as parameters.
        It then calls the update_status_contact method from repository_contacts to update the status of a contact.

    :param body: ContactStatusUpdate: Get the status of the contact from the request body
    :param contact_id: int: Get the contact by id
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: The contact with the updated status
    :doc-author: Trelent
    """
    
    contact = await repository_contacts.update_status_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the contact that is to be removed
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/?first_name={contact_first_name}", response_model=List[ContactResponse])
async def search_contact_by_first_name(contact_first_name: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                                       current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The search_contact_by_first_name function searches for contacts by first name.
        Args:
            contact_first_name (str): The first name of the contact to search for.
            skip (int, optional): The number of records to skip in the result set. Defaults to 0.
            limit (int, optional): The maximum number of records returned in the result set. Defaults to 100.

    :param contact_first_name: str: Specify the first name of the contact to search for
    :param skip: int: Skip a number of records in the database
    :param limit: int: Limit the number of results returned
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :return: A list of contacts that match the search criteria
    :doc-author: Trelent
    """
    
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    results = [contact for contact in contacts if contact_first_name.lower() in contact.first_name.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/?last_name={contact_last_name}", response_model=List[ContactResponse])
async def search_contact_by_last_name(contact_last_name: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                                      current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The search_contact_by_last_name function searches for contacts by last name.

    :param contact_last_name: str: Search for a contact by last name
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of results returned
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    results = [contact for contact in contacts if contact_last_name.lower() in contact.last_name.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/?email={contact_email}", response_model=List[ContactResponse])
async def search_contact_by_email(contact_email: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                                       current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The search_contact_by_first_name function searches for a contact by email.
        The function takes in the following parameters:
            - contact_email (str): The email of the contact to search for.
            - skip (int): Number of contacts to skip before returning results. Default is 0, which returns all results starting from index 0.
            - limit (int): Maximum number of contacts to return per page, default is 100.

    :param contact_email: str: Specify the email of the contact we want to search for
    :param skip: int: Skip a number of records in the database
    :param limit: int: Limit the number of results returned
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :return: A list of contacts
    :doc-author: Trelent
    """
    
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    results = [contact for contact in contacts if contact_email.lower() in contact.email.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/birthday/{days}", response_model=List[ContactResponse])
async def get_birthday_contacts(days: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    
    """
    The get_birthday_contacts function returns a list of contacts that have birthdays within the next X days.

    :param days: int: Get the number of days from today to search for contacts
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A list of contacts whose birthday is in the next x days
    :doc-author: Trelent
    """
    
    current_day = datetime.now()
    end_date = current_day + timedelta(days=days)
    contacts = await db.query(repository_contacts.Contact).filter(
        and_(
            repository_contacts.Contact.user_id == current_user.id,
            extract('month', repository_contacts.Contact.birthday) == extract('month', current_day),
            extract('day', repository_contacts.Contact.birthday) >= current_day.day,
            extract('day', repository_contacts.Contact.birthday) <= end_date.day
        )
    ).offset(skip).limit(limit).all()
    
    if not contacts:
        raise HTTPException(status_code=404, detail="Contacts not found")
    return contacts
