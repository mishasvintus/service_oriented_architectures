import pytest
from pydantic import ValidationError
from user_service.app.schemas import UserCreate, UserUpdate

def test_user_create_valid():
    user = UserCreate(login="test", email="test@example.com", password="password")
    assert user.login == "test"
    assert user.email == "test@example.com"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(login="test", email="invalid-email", password="password")

def test_user_update_valid():
    user = UserUpdate(first_name="Test", last_name="User")
    assert user.first_name == "Test"

def test_user_update_phone_validation():
    user = UserUpdate(phone="+1234567890")
    assert user.phone == "+1234567890"

    with pytest.raises(ValidationError):
        UserUpdate(phone="invalid-phone-number")