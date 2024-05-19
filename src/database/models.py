from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(), nullable=False)
    last_name = Column(String(), nullable=False)
    email = Column(String(), nullable=False, unique=True)
    phone = Column(String(), nullable=False)
    birthday = Column(DateTime())
    other_information = Column(String(), nullable=True)
    done = Column(Boolean, default=False)
