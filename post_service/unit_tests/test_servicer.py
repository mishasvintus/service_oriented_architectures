import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest
import pytest_asyncio
import grpc
from tortoise import Tortoise
from post_service.app.models import Post
from post_service.app.servicer import PostService
from post_service.protos import posts_pb2
from grpc import StatusCode
from google.protobuf.timestamp_pb2 import Timestamp
from uuid import uuid4

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["post_service.app.models"]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

# Фикстура для создания экземпляра сервиса
@pytest.fixture(scope="module")
def service():
    return PostService()

@pytest.mark.asyncio
async def test_create_post(service: PostService):
    request = posts_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test description.",
        author_id=123,
        is_private=False,
        tags=["test", "pytest"]
    )
    
    response = await service.CreatePost(request, None)
    
    assert response.post.title == "Test Post"
    assert response.post.description == "This is a test description."
    assert response.post.author_id == 123
    
    db_post = await Post.get(id=response.post.id)
    assert db_post is not None
    assert db_post.title == "Test Post"
    assert db_post.description == "This is a test description."

@pytest.mark.asyncio
async def test_get_post(service: PostService):
    post = await Post.create(title="Get Me", description="...", author_id=1)
    request = posts_pb2.GetPostRequest(id=str(post.id), requester_id=1)
    response = await service.GetPost(request, None)
    assert response.post.id == str(post.id)

@pytest.mark.asyncio
async def test_get_private_post_permission_denied(service: PostService):
    post = await Post.create(title="Private Post", description="...", author_id=1, is_private=True)
    request = posts_pb2.GetPostRequest(id=str(post.id), requester_id=2) # Другой пользователь
    
    # Используем mock для контекста, чтобы проверить вызов abort
    from unittest.mock import AsyncMock
    mock_context = AsyncMock()
    mock_context.abort = AsyncMock()

    await service.GetPost(request, mock_context)
    mock_context.abort.assert_called_once_with(grpc.StatusCode.PERMISSION_DENIED, "You are not allowed to view this post")

@pytest.mark.asyncio
async def test_get_post_not_found(service: PostService):
    non_existent_id = str(uuid4())
    request = posts_pb2.GetPostRequest(id=non_existent_id, requester_id=1)

    from unittest.mock import AsyncMock
    mock_context = AsyncMock()
    mock_context.abort = AsyncMock()

    await service.GetPost(request, mock_context)
    mock_context.abort.assert_called_once_with(grpc.StatusCode.NOT_FOUND, "Post not found")

@pytest.mark.asyncio
async def test_update_post(service: PostService):
    post = await Post.create(title="Update Me", description="Old", author_id=1)
    request = posts_pb2.UpdatePostRequest(
        id=str(post.id),
        title="Updated Title",
        description="New Description",
        requester_id=1
    )
    response = await service.UpdatePost(request, None)
    assert response.post.title == "Updated Title"
    assert response.post.description == "New Description"

@pytest.mark.asyncio
async def test_update_post_permission_denied(service: PostService):
    post = await Post.create(title="Cannot Update", description="...", author_id=1)
    request = posts_pb2.UpdatePostRequest(id=str(post.id), title="Attempt", requester_id=2)

    from unittest.mock import AsyncMock
    mock_context = AsyncMock()
    mock_context.abort = AsyncMock()

    await service.UpdatePost(request, mock_context)
    mock_context.abort.assert_called_once_with(grpc.StatusCode.PERMISSION_DENIED, "You are not the author of this post")

@pytest.mark.asyncio
async def test_update_post_not_found(service: PostService):
    non_existent_id = str(uuid4())
    request = posts_pb2.UpdatePostRequest(id=non_existent_id, title="Attempt", requester_id=1)

    from unittest.mock import AsyncMock
    mock_context = AsyncMock()
    mock_context.abort = AsyncMock()

    await service.UpdatePost(request, mock_context)
    mock_context.abort.assert_called_once_with(grpc.StatusCode.NOT_FOUND, "Post not found")

@pytest.mark.asyncio
async def test_delete_post(service: PostService):
    post = await Post.create(title="Delete Me", description="...", author_id=1)
    request = posts_pb2.DeletePostRequest(id=str(post.id), requester_id=1)
    await service.DeletePost(request, None)
    
    deleted_post = await Post.get_or_none(id=post.id)
    assert deleted_post is None

@pytest.mark.asyncio
async def test_delete_post_permission_denied(service: PostService):
    post = await Post.create(title="Cannot Delete", description="...", author_id=1)
    request = posts_pb2.DeletePostRequest(id=str(post.id), requester_id=2) # Другой пользователь

    from unittest.mock import AsyncMock
    mock_context = AsyncMock()
    mock_context.abort = AsyncMock()

    await service.DeletePost(request, mock_context)
    mock_context.abort.assert_called_once_with(grpc.StatusCode.PERMISSION_DENIED, "You are not the author of this post")

@pytest.mark.asyncio
async def test_delete_post_not_found(service: PostService):
    non_existent_id = str(uuid4())
    request = posts_pb2.DeletePostRequest(id=non_existent_id, requester_id=1)

    from unittest.mock import AsyncMock
    mock_context = AsyncMock()
    mock_context.abort = AsyncMock()

    await service.DeletePost(request, mock_context)
    mock_context.abort.assert_called_once_with(grpc.StatusCode.NOT_FOUND, "Post not found")

@pytest.mark.asyncio
async def test_list_posts_pagination(service: PostService):
    # Создаем 3 публичных поста
    for i in range(3):
        await Post.create(title=f"Public {i+1}", description="...", author_id=1, is_private=False)
    
    # И один приватный, который не должен попасть в выборку
    await Post.create(title="Private 1", description="...", author_id=1, is_private=True)

    # Запрос первой страницы с размером 2
    request1 = posts_pb2.ListPostsRequest(page=1, page_size=2)
    response1 = await service.ListPosts(request1, None)

    assert len(response1.posts) == 2
    assert response1.total_count == 3 # Всего публичных постов 3
    assert response1.page == 1
    assert response1.page_size == 2

    # Запрос второй страницы с размером 2
    request2 = posts_pb2.ListPostsRequest(page=2, page_size=2)
    response2 = await service.ListPosts(request2, None)

    assert len(response2.posts) == 1 # На второй странице остался 1 пост
    assert response2.total_count == 3
    assert response2.page == 2

    # Проверяем, что ID постов на страницах не пересекаются
    ids1 = {p.id for p in response1.posts}
    ids2 = {p.id for p in response2.posts}
    assert ids1.isdisjoint(ids2)

# TODO: Добавить тесты для каждого метода gRPC 