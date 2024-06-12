import unittest
from unittest.mock import AsyncMock, MagicMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import get_contacts, get_contact,create_contact, remove_contact, update_contact, update_status_contact
from src.schemas.schemas import ContactCreate, ContactUpdate, ContactStatusUpdate

class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, first_name='John', last_name='Doe', email='j@j.com',
                            phone='123456789', birthday='2020-01-01', other_information=None, done=False, user_id=1),
                    Contact(id=2, first_name='Jane', last_name='Doe', email='j@j.com',
                            phone='123456789', birthday='2020-01-01', other_information=None, done=False, user_id=1),
                    Contact(id=3, first_name='John', last_name='Doe', email='j@j.com',
                            phone='123456789', birthday='2020-01-01', other_information=None, done=False, user_id=1)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact(id=1, first_name='John', last_name='Doe', email='j@j.com',
                          phone='123456789', birthday='2020-01-01', other_information=None, done=False, user_id=1)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(1, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactCreate(first_name='John', last_name='Doe', email='j@j.com', phone='123456789',
                             birthday='2020-01-01', other_information=None, done=False)
        result = await create_contact(body, self.user, self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact(self):
        body = ContactUpdate(first_name='Jane', last_name='Doe', email='j@j.com',
                             phone='123456789', birthday='2020-01-01', other_information=None, done=False)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='John', last_name='Doe', email='j@j.com', phone='123456789',
                                                                 birthday='2020-01-01', other_information=None, done=False, user_id=1)
        self.session.execute.return_value = mocked_contact

        result = await update_contact(1, body, self.user, self.session)

        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)
        # self.assertEqual(result.first_name, body.first_name)
        # self.assertEqual(result.last_name, body.last_name)
        # self.assertEqual(result.email, body.email)
        # self.assertEqual(result.phone, body.phone)
        # self.assertEqual(result.birthday.isoformat(), body.birthday)
        # self.assertEqual(result.done, body.done)

    async def test_update_status_contact(self):
        body = ContactStatusUpdate(done=True)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='John', last_name='Doe', email='j@j.com',
                                                                 phone='123456789', birthday='2020-01-01', other_information=None, done=False)
        self.session.execute.return_value = mocked_contact
        result = await update_status_contact(1, body, self.user, self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.done, body.done)

    async def test_remove_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='John', last_name='Doe', email='j@j.com',
                                                                 phone='123456789', birthday='2020-01-01', done=False, user_id=1)
        self.session.execute.return_value = mocked_contact
        result = await remove_contact(1, self.user, self.session)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)
