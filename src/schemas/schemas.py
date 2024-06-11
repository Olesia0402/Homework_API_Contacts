from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime | None
    avatar: str
    confirmed: bool

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: Optional[datetime]
    other_information: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int
    user_id: int
    created_at: datetime


class ContactUpdate(ContactBase):
    done: bool


class ContactStatusUpdate(BaseModel):
    done: bool


class ContactResponse(BaseModel):
    contact: Contact
    detail: str = "Contact successfully created"

    class Config:
        from_attributes = True


class RequestEmail(BaseModel):
    email: EmailStr
