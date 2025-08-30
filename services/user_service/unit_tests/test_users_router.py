import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from user_service.app.main import app
from tortoise import Tortoise

@pytest_asyncio.fixture(scope="module", autouse=True)
async def init_db():
    await Tortoise.init(
        config={
            "connections": {"default": "sqlite://:memory:"},
            "apps": {
                "models": {
                    "models": ["user_service.app.models"],
                    "default_connection": "default",
                }
            },
        }
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest_asyncio.fixture(scope="module")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=True) as client:
        yield client

@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post("/users/register", json={
        "login": "testuser",
        "email": "test@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["login"] == "testuser"
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_duplicate_user_registration(async_client):
    await async_client.post("/users/register", json={
        "login": "duplicateuser",
        "email": "duplicate@example.com",
        "password": "securepassword"
    })
    response = await async_client.post("/users/register", json={
        "login": "duplicateuser",
        "email": "duplicate@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 400
    data = response.json()
    assert "Login or email already registered" in data.get("detail", "")

@pytest.mark.asyncio
async def test_user_login(async_client):
    await async_client.post("/users/register", json={
        "login": "loginuser",
        "email": "login@example.com",
        "password": "securepassword"
    })

    response = await async_client.post("/users/login", data={
        "username": "loginuser",
        "password": "securepassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_update_profile(async_client):

    reg_response = await async_client.post("/users/register", json={
        "login": "updateuser",
        "email": "update@example.com",
        "password": "securepassword"
    })
    assert reg_response.status_code == 201


    login_response = await async_client.post("/users/login", data={
        "username": "updateuser",
        "password": "securepassword"
    })
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}


    update_response = await async_client.put("/users/profile", json={
        "first_name": "Updated",
        "last_name": "User"
    }, headers=headers)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data.get("first_name") == "Updated"
    assert data.get("last_name") == "User"

@pytest.mark.asyncio
async def test_get_profile(async_client):
    reg_response = await async_client.post("/users/register", json={
        "login": "profileuser",
        "email": "profile@example.com",
        "password": "securepassword"
    })
    assert reg_response.status_code == 201

    login_response = await async_client.post("/users/login", data={
        "username": "profileuser",
        "password": "securepassword"
    })
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    profile_response = await async_client.get("/users/profile", headers=headers)
    assert profile_response.status_code == 200
    data = profile_response.json()
    assert data.get("login") == "profileuser"
    assert data.get("email") == "profile@example.com"
