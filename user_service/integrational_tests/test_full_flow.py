import os
import httpx

BASE_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

def test_full_flow():
    # Регистрация пользователя через API Gateway
    register_response = httpx.post(
        f"{BASE_URL}/api/register",
        json={
            "login": "integrationuser",
            "email": "integration@example.com",
            "password": "securepassword"
        }
    )
    assert register_response.status_code == 201, register_response.text
    user_data = register_response.json()
    assert user_data["login"] == "integrationuser"
    assert user_data["email"] == "integration@example.com"

    # Аутентификация: получение токена
    login_response = httpx.post(
        f"{BASE_URL}/api/login",
        data={
            "username": "integrationuser",
            "password": "securepassword"
        }
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json().get("access_token")
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}

    # Получение профиля пользователя
    profile_response = httpx.get(f"{BASE_URL}/api/profile", headers=headers)
    assert profile_response.status_code == 200, profile_response.text
    profile_data = profile_response.json()
    assert profile_data["login"] == "integrationuser"
    assert profile_data["email"] == "integration@example.com"

    # Обновление профиля
    update_response = httpx.put(
        f"{BASE_URL}/api/profile",
        headers=headers,
        json={
            "first_name": "Integration",
            "last_name": "Tester"
        }
    )
    assert update_response.status_code == 200, update_response.text
    updated_data = update_response.json()
    assert updated_data.get("first_name") == "Integration"
    assert updated_data.get("last_name") == "Tester"
