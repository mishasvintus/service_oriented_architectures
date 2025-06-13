import os
import httpx
import pytest
import time

BASE_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

@pytest.fixture(scope="module")
def test_data():
    return {
        "user1": {
            "login": f"api_user1_{os.urandom(4).hex()}",
            "email": f"api_user1_{os.urandom(4).hex()}@example.com",
            "password": "password123"
        },
        "user2": {
            "login": f"api_user2_{os.urandom(4).hex()}",
            "email": f"api_user2_{os.urandom(4).hex()}@example.com",
            "password": "password456"
        },
        "token1": None,
        "token2": None,
        "post_id": None
    }

@pytest.mark.dependency()
def test_setup_users(test_data):
    """Регистрируем и логиним двух пользователей для тестов"""
    # Регистрация пользователя 1
    reg_resp1 = httpx.post(f"{BASE_URL}/api/register", json=test_data["user1"])
    assert reg_resp1.status_code == 201
    
    # Логин пользователя 1
    login_resp1 = httpx.post(f"{BASE_URL}/api/login", data={
        "username": test_data["user1"]["login"],
        "password": test_data["user1"]["password"]
    })
    assert login_resp1.status_code == 200
    test_data["token1"] = login_resp1.json()["access_token"]
    
    # Регистрация пользователя 2
    reg_resp2 = httpx.post(f"{BASE_URL}/api/register", json=test_data["user2"])
    assert reg_resp2.status_code == 201
    
    # Логин пользователя 2
    login_resp2 = httpx.post(f"{BASE_URL}/api/login", data={
        "username": test_data["user2"]["login"],
        "password": test_data["user2"]["password"]
    })
    assert login_resp2.status_code == 200
    test_data["token2"] = login_resp2.json()["access_token"]

@pytest.mark.dependency(depends=["test_setup_users"])
def test_create_post_for_testing(test_data):
    """Создаем пост для тестирования новых функций"""
    headers = {"Authorization": f"Bearer {test_data['token1']}"}
    post_data = {
        "title": "Test Post for New Features",
        "description": "This post will be used to test view, like, and comment features",
        "is_private": False,
        "tags": ["test", "features"]
    }
    
    response = httpx.post(f"{BASE_URL}/api/posts", headers=headers, json=post_data)
    assert response.status_code == 200
    
    data = response.json()
    test_data["post_id"] = data["id"]
    assert data["title"] == "Test Post for New Features"

@pytest.mark.dependency(depends=["test_create_post_for_testing"])
def test_view_post_functionality(test_data):
    """Тест функции просмотра поста"""
    headers = {"Authorization": f"Bearer {test_data['token2']}"}
    
    # Пользователь 2 просматривает пост пользователя 1
    response = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/view", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Post viewed successfully"

@pytest.mark.dependency(depends=["test_view_post_functionality"])
def test_like_post_functionality(test_data):
    """Тест функции лайка поста"""
    headers = {"Authorization": f"Bearer {test_data['token2']}"}
    
    # Пользователь 2 лайкает пост
    response = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/like", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Post liked successfully"
    assert data["total_likes"] == 1

@pytest.mark.dependency(depends=["test_like_post_functionality"])
def test_duplicate_like_prevention(test_data):
    """Тест предотвращения повторного лайка"""
    headers = {"Authorization": f"Bearer {test_data['token2']}"}
    
    # Попытка повторного лайка
    response = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/like", headers=headers)
    assert response.status_code == 409  # Conflict

@pytest.mark.dependency(depends=["test_duplicate_like_prevention"])
def test_unlike_post_functionality(test_data):
    """Тест функции убирания лайка"""
    headers = {"Authorization": f"Bearer {test_data['token2']}"}
    
    # Убираем лайк
    response = httpx.delete(f"{BASE_URL}/api/posts/{test_data['post_id']}/like", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Post unliked successfully"
    assert data["total_likes"] == 0

@pytest.mark.dependency(depends=["test_unlike_post_functionality"])
def test_unlike_not_liked_post(test_data):
    """Тест убирания лайка с поста который не лайкали"""
    headers = {"Authorization": f"Bearer {test_data['token2']}"}
    
    # Попытка убрать несуществующий лайк
    response = httpx.delete(f"{BASE_URL}/api/posts/{test_data['post_id']}/like", headers=headers)
    assert response.status_code == 404  # Not Found

@pytest.mark.dependency(depends=["test_unlike_not_liked_post"])
def test_comment_post_functionality(test_data):
    """Тест функции комментирования поста"""
    headers = {"Authorization": f"Bearer {test_data['token2']}"}
    comment_data = {"content": "This is a great post! Thanks for sharing."}
    
    response = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/comments", 
                         headers=headers, json=comment_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comment added successfully"
    assert data["comment"]["content"] == "This is a great post! Thanks for sharing."
    
    test_data["comment_id"] = data["comment"]["id"]

@pytest.mark.dependency(depends=["test_comment_post_functionality"])
def test_get_post_comments(test_data):
    """Тест получения комментариев поста"""
    # Получаем комментарии (без авторизации - публичный endpoint)
    response = httpx.get(f"{BASE_URL}/api/posts/{test_data['post_id']}/comments?page=1&page_size=10")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] >= 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["comments"]) >= 1
    assert data["comments"][0]["content"] == "This is a great post! Thanks for sharing."

@pytest.mark.dependency(depends=["test_get_post_comments"])
def test_multiple_comments_and_pagination(test_data):
    """Тест множественных комментариев и пагинации"""
    headers1 = {"Authorization": f"Bearer {test_data['token1']}"}
    headers2 = {"Authorization": f"Bearer {test_data['token2']}"}
    
    # Добавляем несколько комментариев от разных пользователей
    comments = [
        ("Comment from user 1", headers1),
        ("Another comment from user 2", headers2),
        ("Third comment from user 1", headers1),
        ("Fourth comment from user 2", headers2),
    ]
    
    for content, headers in comments:
        comment_data = {"content": content}
        response = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/comments", 
                             headers=headers, json=comment_data)
        assert response.status_code == 200
    
    # Проверяем пагинацию - первая страница с 3 комментариями
    response = httpx.get(f"{BASE_URL}/api/posts/{test_data['post_id']}/comments?page=1&page_size=3")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] >= 5  # Минимум 5 комментариев
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["comments"]) == 3
    
    # Вторая страница
    response = httpx.get(f"{BASE_URL}/api/posts/{test_data['post_id']}/comments?page=2&page_size=3")
    assert response.status_code == 200
    
    data = response.json()
    assert data["page"] == 2
    assert len(data["comments"]) >= 2

@pytest.mark.dependency(depends=["test_multiple_comments_and_pagination"])
def test_cross_user_interactions(test_data):
    """Тест взаимодействий между пользователями"""
    headers1 = {"Authorization": f"Bearer {test_data['token1']}"}
    headers2 = {"Authorization": f"Bearer {test_data['token2']}"}
    
    # Оба пользователя лайкают пост
    like_resp1 = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/like", headers=headers1)
    assert like_resp1.status_code == 200
    assert like_resp1.json()["total_likes"] == 1
    
    like_resp2 = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/like", headers=headers2)
    assert like_resp2.status_code == 200
    assert like_resp2.json()["total_likes"] == 2
    
    # Оба пользователя просматривают пост
    view_resp1 = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/view", headers=headers1)
    assert view_resp1.status_code == 200
    
    view_resp2 = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/view", headers=headers2)
    assert view_resp2.status_code == 200

def test_unauthorized_access_to_new_features(test_data):
    """Тест доступа к новым функциям без авторизации"""
    post_id = "dummy-post-id"
    
    # Просмотр поста без токена
    view_resp = httpx.post(f"{BASE_URL}/api/posts/{post_id}/view")
    assert view_resp.status_code == 401
    
    # Лайк поста без токена
    like_resp = httpx.post(f"{BASE_URL}/api/posts/{post_id}/like")
    assert like_resp.status_code == 401
    
    # Комментирование без токена
    comment_resp = httpx.post(f"{BASE_URL}/api/posts/{post_id}/comments", 
                             json={"content": "test"})
    assert comment_resp.status_code == 401

@pytest.mark.dependency(depends=["test_setup_users"])
def test_invalid_post_id_handling(test_data):
    """Тест обработки несуществующих постов"""
    headers = {"Authorization": f"Bearer {test_data['token1']}"}
    invalid_post_id = "00000000-0000-0000-0000-000000000000"  # Valid UUID but non-existent
    
    # Просмотр несуществующего поста
    view_resp = httpx.post(f"{BASE_URL}/api/posts/{invalid_post_id}/view", headers=headers)
    assert view_resp.status_code == 404
    
    # Лайк несуществующего поста
    like_resp = httpx.post(f"{BASE_URL}/api/posts/{invalid_post_id}/like", headers=headers)
    assert like_resp.status_code == 404
    
    # Комментирование несуществующего поста
    comment_resp = httpx.post(f"{BASE_URL}/api/posts/{invalid_post_id}/comments", 
                             headers=headers, json={"content": "test"})
    assert comment_resp.status_code == 404

@pytest.mark.dependency(depends=["test_create_post_for_testing"])
def test_comment_validation(test_data):
    """Тест валидации комментариев"""
    headers = {"Authorization": f"Bearer {test_data['token1']}"}
    
    # Пустой комментарий
    empty_comment = {"content": ""}
    response = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/comments", 
                         headers=headers, json=empty_comment)
    assert response.status_code == 422  # Validation error
    
    # Комментарий только из пробелов
    whitespace_comment = {"content": "   "}
    response = httpx.post(f"{BASE_URL}/api/posts/{test_data['post_id']}/comments", 
                         headers=headers, json=whitespace_comment)
    assert response.status_code == 422  # Validation error 