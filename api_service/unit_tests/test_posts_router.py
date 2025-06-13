import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest
from fastapi.testclient import TestClient
from api_service.app.main import app
from api_service.app.routers.posts_router import router
from api_service.app.auth import get_current_user_id
from api_service.app.grpc_client import get_posts_stub


class TestPostsRouter(unittest.TestCase):
    
    def setUp(self):
        self.mock_user_id = 123
        self.mock_post_id = "test-post-id"
        
        # Override dependency для авторизации
        def mock_get_current_user_id():
            return self.mock_user_id
        
        # Override dependency для gRPC stub
        def mock_get_posts_stub():
            return self.mock_stub
        
        app.dependency_overrides[get_current_user_id] = mock_get_current_user_id
        app.dependency_overrides[get_posts_stub] = mock_get_posts_stub
        
        self.client = TestClient(app)
        self.mock_token = "mock_jwt_token"
        self.mock_stub = Mock()
    
    def tearDown(self):
        # Очищаем dependency overrides
        app.dependency_overrides.clear()
    
    def _get_auth_headers(self):
        return {"Authorization": f"Bearer {self.mock_token}"}
    
    @patch('api_service.app.routers.posts_router.MessageToDict')
    def test_view_post_success(self, mock_message_to_dict):
        """Тест успешного просмотра поста через API Gateway"""
        
        mock_message_to_dict.return_value = {
            "success": True,
            "message": "Post viewed successfully"
        }
        
        mock_response = Mock()
        self.mock_stub.ViewPost.return_value = mock_response
        
        response = self.client.post(
            f"/api/posts/{self.mock_post_id}/view",
            headers=self._get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Post viewed successfully")
    
    @patch('api_service.app.routers.posts_router.MessageToDict')
    def test_like_post_success(self, mock_message_to_dict):
        """Тест успешного лайка поста через API Gateway"""
        
        mock_message_to_dict.return_value = {
            "success": True,
            "message": "Post liked successfully",
            "total_likes": 5
        }
        
        mock_response = Mock()
        self.mock_stub.LikePost.return_value = mock_response
        
        response = self.client.post(
            f"/api/posts/{self.mock_post_id}/like",
            headers=self._get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Post liked successfully")
        self.assertEqual(data["total_likes"], 5)
    
    @patch('api_service.app.routers.posts_router.MessageToDict')
    def test_unlike_post_success(self, mock_message_to_dict):
        """Тест успешного убирания лайка через API Gateway"""
        
        mock_message_to_dict.return_value = {
            "success": True,
            "message": "Post unliked successfully",
            "total_likes": 3
        }
        
        mock_response = Mock()
        self.mock_stub.UnlikePost.return_value = mock_response
        
        response = self.client.delete(
            f"/api/posts/{self.mock_post_id}/like",
            headers=self._get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Post unliked successfully")
        self.assertEqual(data["total_likes"], 3)
    
    @patch('api_service.app.routers.posts_router.MessageToDict')
    def test_comment_post_success(self, mock_message_to_dict):
        """Тест успешного добавления комментария через API Gateway"""
        
        mock_message_to_dict.return_value = {
            "success": True,
            "message": "Comment added successfully",
            "comment": {
                "id": 456,
                "post_id": self.mock_post_id,
                "user_id": self.mock_user_id,
                "content": "Great post!",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }
        
        mock_response = Mock()
        self.mock_stub.CommentPost.return_value = mock_response
        
        comment_data = {"content": "Great post!"}
        response = self.client.post(
            f"/api/posts/{self.mock_post_id}/comments",
            headers=self._get_auth_headers(),
            json=comment_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Comment added successfully")
        self.assertEqual(data["comment"]["content"], "Great post!")
    
    @patch('api_service.app.routers.posts_router.MessageToDict')
    def test_get_post_comments_success(self, mock_message_to_dict):
        """Тест успешного получения комментариев через API Gateway"""
        
        mock_message_to_dict.return_value = {
            "comments": [
                {
                    "id": 1,
                    "post_id": self.mock_post_id,
                    "user_id": 100,
                    "content": "Comment 1",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z"
                },
                {
                    "id": 2,
                    "post_id": self.mock_post_id,
                    "user_id": 101,
                    "content": "Comment 2",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z"
                },
                {
                    "id": 3,
                    "post_id": self.mock_post_id,
                    "user_id": 102,
                    "content": "Comment 3",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z"
                }
            ],
            "total_count": 10,
            "page": 1,
            "page_size": 5
        }
        
        mock_response = Mock()
        self.mock_stub.GetPostComments.return_value = mock_response
        
        response = self.client.get(
            f"/api/posts/{self.mock_post_id}/comments?page=1&page_size=5"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["comments"]), 3)
        self.assertEqual(data["total_count"], 10)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 5)
    
    def test_view_post_unauthorized(self):
        """Тест просмотра поста без авторизации"""
        # Временно убираем dependency override для этого теста
        app.dependency_overrides.clear()
        client = TestClient(app)
        response = client.post(f"/api/posts/{self.mock_post_id}/view")
        self.assertEqual(response.status_code, 401)
        # Восстанавливаем dependency override
        app.dependency_overrides[get_current_user_id] = lambda: self.mock_user_id
        app.dependency_overrides[get_posts_stub] = lambda: self.mock_stub
    
    def test_like_post_unauthorized(self):
        """Тест лайка поста без авторизации"""
        # Временно убираем dependency override для этого теста
        app.dependency_overrides.clear()
        client = TestClient(app)
        response = client.post(f"/api/posts/{self.mock_post_id}/like")
        self.assertEqual(response.status_code, 401)
        # Восстанавливаем dependency override
        app.dependency_overrides[get_current_user_id] = lambda: self.mock_user_id
        app.dependency_overrides[get_posts_stub] = lambda: self.mock_stub
    
    def test_comment_post_unauthorized(self):
        """Тест комментирования поста без авторизации"""
        # Временно убираем dependency override для этого теста
        app.dependency_overrides.clear()
        client = TestClient(app)
        comment_data = {"content": "Test comment"}
        response = client.post(
            f"/api/posts/{self.mock_post_id}/comments",
            json=comment_data
        )
        self.assertEqual(response.status_code, 401)
        # Восстанавливаем dependency override
        app.dependency_overrides[get_current_user_id] = lambda: self.mock_user_id
        app.dependency_overrides[get_posts_stub] = lambda: self.mock_stub
    
    def test_comment_post_empty_content(self):
        """Тест комментирования с пустым содержимым"""
        comment_data = {"content": ""}
        response = self.client.post(
            f"/api/posts/{self.mock_post_id}/comments",
            headers=self._get_auth_headers(),
            json=comment_data
        )
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_grpc_error_handling(self):
        """Тест обработки gRPC ошибок"""
        import grpc
        
        class MockRpcError(grpc.RpcError):
            def code(self):
                return grpc.StatusCode.UNAVAILABLE
            
            def details(self):
                return "Service unavailable"
        
        self.mock_stub.ViewPost.side_effect = MockRpcError()
        
        response = self.client.post(
            f"/api/posts/{self.mock_post_id}/view",
            headers=self._get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main() 