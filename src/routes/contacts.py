from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.schemas import ContactModel, ContactResponse, ContactStatusUpdate, ContactUpdate
from src.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=["contacts"])


class SomeDuplicateEmailException(Exception):
    pass


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    try:
        return await repository_contacts.create_contact(body, db)
    except SomeDuplicateEmailException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or number value is not unique")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_status_contact(body: ContactStatusUpdate, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_status_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/?first_name={contact_first_name}", response_model=List[ContactResponse])
async def search_contact_by_first_name(contact_first_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    results = [contact for contact in contacts if contact_first_name.lower() in contact.first_name.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/?last_name={contact_last_name}", response_model=List[ContactResponse])
async def search_contact_by_last_name(contact_last_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    results = [contact for contact in contacts if contact_last_name.lower() in contact.last_name.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/?email={contact_email}", response_model=List[ContactResponse])
async def search_contact_by_first_name(contact_email: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    results = [contact for contact in contacts if contact_email.lower() in contact.email.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="Contact not found")
    return results


@router.get("/birthday/{days}", response_model=List[ContactResponse])
async def get_birthday_contacts(days: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    current_day = datetime.now()
    results = []
    for contact in contacts:
        date = current_day + timedelta(days=days)
        if current_day >= contact.birthday <= date:
            results.append(contact)
    if not results:
        raise HTTPException(status_code=404, detail="Contacts not found")
    return results
