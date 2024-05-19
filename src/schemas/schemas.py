from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class ContactModel(BaseModel):
    first_name: str = Field()
    last_name: str = Field()
    email: str = EmailStr()
    phone: str = Field()
    birthday: Optional[datetime] = Field(datetime.date)
    other_information: Optional[str] = Field(None, description="Additional information about the contact")


class ContactUpdate(ContactModel):
    done: bool


class ContactStatusUpdate(ContactModel):
    done: bool


class ContactResponse(ContactModel):
    id: int

    class Config:
        orm_mode = True
