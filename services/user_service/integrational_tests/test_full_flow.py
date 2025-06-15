import os
import httpx
import pytest

BASE_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

UNIQUE_LOGIN = f"integrationuser_{os.urandom(4).hex()}"
UNIQUE_EMAIL = f"integration_{os.urandom(4).hex()}@example.com"

@pytest.fixture(scope="module")
def user_credentials():
    """Фикстура для хранения данных пользователя в течение сессии."""
    return {
        "login": UNIQUE_LOGIN,
        "email": UNIQUE_EMAIL,
        "password": "securepassword"
    }

@pytest.mark.dependency()
def test_register_user(user_credentials):
    """Тест регистрации нового пользователя."""
    response = httpx.post(
        f"{BASE_URL}/api/register",
        json={
            "login": user_credentials["login"],
            "email": user_credentials["email"],
            "password": user_credentials["password"]
        }
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["login"] == user_credentials["login"]
    assert data["email"] == user_credentials["email"]

@pytest.mark.dependency(depends=["test_register_user"])
def test_login_and_get_token(user_credentials):
    """Тест аутентификации и получения токена."""
    response = httpx.post(
        f"{BASE_URL}/api/login",
        data={
            "username": user_credentials["login"],
            "password": user_credentials["password"]
        }
    )
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token is not None
    # Сохраняем токен для следующих тестов
    user_credentials["token"] = token

@pytest.mark.dependency(depends=["test_login_and_get_token"])
def test_get_user_profile(user_credentials):
    """Тест получения профиля пользователя."""
    headers = {"Authorization": f"Bearer {user_credentials['token']}"}
    response = httpx.get(f"{BASE_URL}/api/profile", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["login"] == user_credentials["login"]

@pytest.mark.dependency(depends=["test_login_and_get_token"])
def test_update_user_profile(user_credentials):
    """Тест обновления профиля пользователя."""
    headers = {"Authorization": f"Bearer {user_credentials['token']}"}
    update_data = {
        "first_name": "Integration",
        "last_name": "Tester"
    }
    response = httpx.put(f"{BASE_URL}/api/profile", headers=headers, json=update_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Integration"
    assert data["last_name"] == "Tester"

@pytest.mark.dependency(depends=["test_login_and_get_token"])
def test_delete_user_profile(user_credentials):
    """Тест удаления профиля пользователя."""
    headers = {"Authorization": f"Bearer {user_credentials['token']}"}
    response = httpx.delete(f"{BASE_URL}/api/profile", headers=headers)
    assert response.status_code == 204, response.text

    # Проверяем, что пользователь больше не может войти в систему
    login_response = httpx.post(
        f"{BASE_URL}/api/login",
        data={
            "username": user_credentials["login"],
            "password": user_credentials["password"]
        }
    )
    assert login_response.status_code == 400
