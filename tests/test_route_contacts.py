# from unittest.mock import Mock, patch

# import pytest

# from src.services.auth import auth_service
# from src.database.models import Contact

# def test_get_contacts(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, list)

# def test_get_contact(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/1", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, dict)
#     assert "id" in data

# def test_get_contact_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/100", headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Contact not found"

# def test_create_contact(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.post("api/contacts",
#                             json={"first_name": "test", "last_name": "test", "email": "test", "phone": "test", "birthday": "2000-06-12"},
#                             headers=headers)
#     assert response.status_code == 201, response.text
#     data = response.json()
#     assert "id" in data
#     assert data["first_name"] == "test"
#     assert data["last_name"] == "test"
#     assert data["email"] == "test"
#     assert data["phone"] == "test"
#     assert data["birthday"] == "test"

# def test_create_contact_bad_request(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.post("api/contacts",
#                             json={"first_name": "test", "last_name": "test"},
#                             headers=headers)
#     assert response.status_code == 500, response.text
#     data = response.json()
#     assert "detail" in data

# def test_create_contact_value_not_unique(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.post("api/contacts",
#                             json={"first_name": "test", "last_name": "test", "email": "test@test.com", "phone": "test", "birthday": "test"},
#                             headers=headers)
#     assert response.status_code == 400, response.text
#     data = response.json()
#     assert data["detail"] == "Email or number value is not unique"

# def test_update_contact(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.put("api/contacts/1",
#                             json={"first_name": "test1", "last_name": "test1",
#                                   "email": "test1@test.com", "phone": "test1",
#                                   "birthday": "1996-06-11", "done": True},
#                             headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert "id" in data
#     assert data["first_name"] == "test1"
#     assert data["last_name"] == "test1"
#     assert data["email"] == "test1"
#     assert data["phone"] == "test1"
#     assert data["birthday"] == "test1"

# def test_update_contact_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.put("api/contacts/100",
#                             json={"first_name": "test1", "last_name": "test1",
#                                   "email": "test1@test.com", "phone": "test1",
#                                   "birthday": "1996-06-11", "done": True},
#                             headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     # assert data["detail"] == "Contact not found"

# def test_update_status_contact(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.patch("api/contacts/1",
#                             json={"done": True},
#                             headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert "id" in data
#     assert data["done"] == True

# def test_update_status_contact_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.patch("api/contacts/100",
#                             json={"done": True},
#                             headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Contact not found"

# def test_delete_contact(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.delete("api/contacts/1", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert "id" in data

# def test_delete_contact_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.delete("api/contacts/100", headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Contact not found"

# def test_search_contact_by_first_name(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/?first_name=test", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, Contact)

# def test_search_contact_by_first_name_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/?first_name=test1", headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Contact not found"

# def test_search_contact_by_last_name(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/?last_name=test", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, Contact)

# def test_search_contact_contact_by_last_name_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/?last_name=test1", headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Contact not found"

# def test_search_contact_by_email(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/?email=test", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, Contact)

# def test_search_contact_by_email_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/?email=test1", headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Contact not found"

# def test_get_birthday_contacts(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/birthdays/1", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, list)

# def test_get_birthday_contacts_not_found(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/contacts/birthdays/100", headers=headers)
#     assert response.status_code == 404, response.text
#     data = response.json()
#     # assert data["detail"] == "Contact not found"