import pytest
from pydantic import ValidationError
from user_service.app.schemas.user import UserCreate, UserUpdate

def test_user_create_valid():
    user = UserCreate(login="testuser", email="test@example.com", password="securepassword")
    assert user.login == "testuser"
    assert user.email == "test@example.com"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(login="testuser", email="invalid-email", password="securepassword")

def test_user_update_valid():
    user_update = UserUpdate(first_name="John", last_name="Doe")
    assert user_update.first_name == "John"
    assert user_update.last_name == "Doe"

def test_user_update_invalid_phone():
    with pytest.raises(ValidationError):
        UserUpdate(phone="invalid-phone-number") 

def test_user_update_valid_phone():
    user_update = UserUpdate(phone="+1234567890") 
    assert user_update.phone == "+1234567890"