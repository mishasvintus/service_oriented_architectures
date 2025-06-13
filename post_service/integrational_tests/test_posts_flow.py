import os
import httpx
import pytest

BASE_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

@pytest.fixture(scope="module")
def shared_data():
    return {
        "user": {
            "login": f"post_tester_{os.urandom(4).hex()}",
            "email": f"post_tester_{os.urandom(4).hex()}@example.com",
            "password": "securepassword"
        },
        "token": None,
        "post_id": None
    }

@pytest.mark.dependency()
def test_register_and_login(shared_data):
    """Сначала регистрируем и логиним пользователя, чтобы получить токен."""
    # Регистрация
    reg_response = httpx.post(f"{BASE_URL}/api/register", json=shared_data["user"])
    assert reg_response.status_code == 201

    # Логин
    login_payload = {
        "username": shared_data["user"]["login"],
        "password": shared_data["user"]["password"]
    }
    login_response = httpx.post(f"{BASE_URL}/api/login", data=login_payload)
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    assert token is not None
    shared_data["token"] = token

@pytest.mark.dependency(depends=["test_register_and_login"])
def test_create_post(shared_data):
    """Тест создания поста."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    post_data = {
        "title": "My First Post",
        "description": "Hello, world!",
        "is_private": False,
        "tags": ["testing", "api"]
    }
    response = httpx.post(f"{BASE_URL}/api/posts", headers=headers, json=post_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "My First Post"
    assert data["description"] == "Hello, world!"
    shared_data["post_id"] = data["id"]

@pytest.mark.dependency(depends=["test_create_post"])
def test_get_post(shared_data):
    """Тест получения поста."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    response = httpx.get(f"{BASE_URL}/api/posts/{shared_data['post_id']}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == shared_data["post_id"]

@pytest.mark.dependency(depends=["test_get_post"])
def test_view_post(shared_data):
    """Тест просмотра поста (новая функция)."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    response = httpx.post(f"{BASE_URL}/api/posts/{shared_data['post_id']}/view", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Post viewed successfully"

@pytest.mark.dependency(depends=["test_view_post"])
def test_like_post(shared_data):
    """Тест лайка поста (новая функция)."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    response = httpx.post(f"{BASE_URL}/api/posts/{shared_data['post_id']}/like", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Post liked successfully"
    assert data["total_likes"] == 1

@pytest.mark.dependency(depends=["test_like_post"])
def test_like_post_duplicate(shared_data):
    """Тест повторного лайка поста (должен вернуть ошибку)."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    response = httpx.post(f"{BASE_URL}/api/posts/{shared_data['post_id']}/like", headers=headers)
    assert response.status_code == 409, response.text  # Conflict

@pytest.mark.dependency(depends=["test_like_post_duplicate"])
def test_unlike_post(shared_data):
    """Тест убирания лайка поста (новая функция)."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    response = httpx.delete(f"{BASE_URL}/api/posts/{shared_data['post_id']}/like", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Post unliked successfully"
    assert data["total_likes"] == 0

@pytest.mark.dependency(depends=["test_unlike_post"])
def test_unlike_post_not_liked(shared_data):
    """Тест убирания лайка с поста который не лайкали."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    response = httpx.delete(f"{BASE_URL}/api/posts/{shared_data['post_id']}/like", headers=headers)
    assert response.status_code == 404, response.text  # Not Found

@pytest.mark.dependency(depends=["test_unlike_post_not_liked"])
def test_comment_post(shared_data):
    """Тест добавления комментария к посту (новая функция)."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    comment_data = {"content": "This is a great post!"}
    response = httpx.post(f"{BASE_URL}/api/posts/{shared_data['post_id']}/comments", 
                         headers=headers, json=comment_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comment added successfully"
    assert data["comment"]["content"] == "This is a great post!"
    shared_data["comment_id"] = data["comment"]["id"]

@pytest.mark.dependency(depends=["test_comment_post"])
def test_get_post_comments(shared_data):
    """Тест получения комментариев поста с пагинацией (новая функция)."""
    response = httpx.get(f"{BASE_URL}/api/posts/{shared_data['post_id']}/comments?page=1&page_size=10")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_count"] >= 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["comments"]) >= 1
    assert data["comments"][0]["content"] == "This is a great post!"

@pytest.mark.dependency(depends=["test_get_post_comments"])
def test_add_multiple_comments(shared_data):
    """Тест добавления нескольких комментариев для проверки пагинации."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    
    for i in range(2, 6):  
        comment_data = {"content": f"Comment number {i}"}
        response = httpx.post(f"{BASE_URL}/api/posts/{shared_data['post_id']}/comments", 
                             headers=headers, json=comment_data)
        assert response.status_code == 200, response.text

@pytest.mark.dependency(depends=["test_add_multiple_comments"])
def test_comments_pagination(shared_data):
    """Тест пагинации комментариев."""
    # Получаем первую страницу с 3 комментариями
    response = httpx.get(f"{BASE_URL}/api/posts/{shared_data['post_id']}/comments?page=1&page_size=3")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_count"] >= 5
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["comments"]) == 3
    
    # Получаем вторую страницу
    response = httpx.get(f"{BASE_URL}/api/posts/{shared_data['post_id']}/comments?page=2&page_size=3")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["page"] == 2
    assert len(data["comments"]) >= 2

@pytest.mark.dependency(depends=["test_comments_pagination"])
def test_update_post(shared_data):
    """Тест обновления поста."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    update_data = {"title": "Updated Title", "description": "Updated content."}
    response = httpx.put(f"{BASE_URL}/api/posts/{shared_data['post_id']}", headers=headers, json=update_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated content."

@pytest.mark.dependency(depends=["test_update_post"])
def test_delete_post(shared_data):
    """Тест удаления поста."""
    headers = {"Authorization": f"Bearer {shared_data['token']}"}
    response = httpx.delete(f"{BASE_URL}/api/posts/{shared_data['post_id']}", headers=headers)
    assert response.status_code == 204, response.text

    # Проверяем, что пост действительно удален
    response_get = httpx.get(f"{BASE_URL}/api/posts/{shared_data['post_id']}", headers=headers)
    assert response_get.status_code == 404

def test_access_control():
    """
    Проверяет контроль доступа:
    1. Запросы без токена должны падать с 401.
    2. Один пользователь не может изменять пост другого (403).
    """
    # 1. Проверка доступа без токена
    post_data = {"title": "test", "description": "test"}
    response_no_token = httpx.post(f"{BASE_URL}/api/posts", json=post_data)
    assert response_no_token.status_code == 401

    # 2. Создаем двух пользователей
    user_a_data = {
        "login": f"user_a_{os.urandom(4).hex()}",
        "email": f"user_a_{os.urandom(4).hex()}@example.com",
        "password": "password_a"
    }
    user_b_data = {
        "login": f"user_b_{os.urandom(4).hex()}",
        "email": f"user_b_{os.urandom(4).hex()}@example.com",
        "password": "password_b"
    }

    # Регистрация и логин user_A
    httpx.post(f"{BASE_URL}/api/register", json=user_a_data)
    login_a_resp = httpx.post(f"{BASE_URL}/api/login", data={"username": user_a_data["login"], "password": user_a_data["password"]})
    token_a = login_a_resp.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Регистрация и логин user_B
    httpx.post(f"{BASE_URL}/api/register", json=user_b_data)
    login_b_resp = httpx.post(f"{BASE_URL}/api/login", data={"username": user_b_data["login"], "password": user_b_data["password"]})
    token_b = login_b_resp.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User_A создает ПРИВАТНЫЙ пост
    private_post_data = {"title": "private post", "description": "secret", "is_private": True}
    create_resp = httpx.post(f"{BASE_URL}/api/posts", headers=headers_a, json=private_post_data)
    assert create_resp.status_code == 200
    post_id = create_resp.json()["id"]

    # User_B пытается получить, обновить и удалить пост User_A
    response_get = httpx.get(f"{BASE_URL}/api/posts/{post_id}", headers=headers_b)
    assert response_get.status_code == 403

    response_update = httpx.put(f"{BASE_URL}/api/posts/{post_id}", headers=headers_b, json={"title": "hacked"})
    assert response_update.status_code == 403

    response_delete = httpx.delete(f"{BASE_URL}/api/posts/{post_id}", headers=headers_b)
    assert response_delete.status_code == 403

def test_new_features_access_control():
    """Тест контроля доступа для новых функций."""
    # Создаем двух пользователей
    user_a_data = {
        "login": f"owner_{os.urandom(4).hex()}",
        "email": f"owner_{os.urandom(4).hex()}@example.com",
        "password": "password_a"
    }
    user_b_data = {
        "login": f"viewer_{os.urandom(4).hex()}",
        "email": f"viewer_{os.urandom(4).hex()}@example.com",
        "password": "password_b"
    }

    # Регистрация и логин обоих пользователей
    httpx.post(f"{BASE_URL}/api/register", json=user_a_data)
    login_a_resp = httpx.post(f"{BASE_URL}/api/login", data={"username": user_a_data["login"], "password": user_a_data["password"]})
    token_a = login_a_resp.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    httpx.post(f"{BASE_URL}/api/register", json=user_b_data)
    login_b_resp = httpx.post(f"{BASE_URL}/api/login", data={"username": user_b_data["login"], "password": user_b_data["password"]})
    token_b = login_b_resp.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User_A создает публичный пост
    public_post_data = {"title": "public post", "description": "everyone can see", "is_private": False}
    create_resp = httpx.post(f"{BASE_URL}/api/posts", headers=headers_a, json=public_post_data)
    assert create_resp.status_code == 200
    post_id = create_resp.json()["id"]

    # User_B может просматривать публичный пост
    view_resp = httpx.post(f"{BASE_URL}/api/posts/{post_id}/view", headers=headers_b)
    assert view_resp.status_code == 200

    # User_B может лайкать публичный пост
    like_resp = httpx.post(f"{BASE_URL}/api/posts/{post_id}/like", headers=headers_b)
    assert like_resp.status_code == 200

    # User_B может комментировать публичный пост
    comment_resp = httpx.post(f"{BASE_URL}/api/posts/{post_id}/comments", 
                             headers=headers_b, json={"content": "Nice post!"})
    assert comment_resp.status_code == 200

    # Проверяем что комментарии доступны всем (без авторизации)
    comments_resp = httpx.get(f"{BASE_URL}/api/posts/{post_id}/comments")
    assert comments_resp.status_code == 200 