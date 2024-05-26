from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract

from src.database.db import get_db
from src.database.models import User
from src.schemas.schemas import ContactCreate, ContactResponse, ContactStatusUpdate, ContactUpdate
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


class SomeDuplicateEmailException(Exception):
    pass


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    try:
        return await repository_contacts.create_contact(body, current_user, db)
    except SomeDuplicateEmailException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or number value is not unique")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_status_contact(body: ContactStatusUpdate, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_status_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/?first_name={contact_first_name}", response_model=List[ContactResponse])
async def search_contact_by_first_name(contact_first_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    results = [contact for contact in contacts if contact_first_name.lower() in contact.first_name.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/?last_name={contact_last_name}", response_model=List[ContactResponse])
async def search_contact_by_last_name(contact_last_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    results = [contact for contact in contacts if contact_last_name.lower() in contact.last_name.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/?email={contact_email}", response_model=List[ContactResponse])
async def search_contact_by_first_name(contact_email: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    results = [contact for contact in contacts if contact_email.lower() in contact.email.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/birthday/{days}", response_model=List[ContactResponse])
async def get_birthday_contacts(days: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
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
