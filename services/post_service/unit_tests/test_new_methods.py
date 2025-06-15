import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest
from post_service.app.servicer import PostService
from post_service.protos import posts_pb2
import grpc


class TestPostServiceNewMethods(unittest.TestCase):
    
    def setUp(self):
        self.service = PostService()
        self.context = Mock()
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostView')
    @patch('post_service.app.servicer.kafka_producer')
    async def test_view_post_success(self, mock_kafka, mock_post_view, mock_post):
        """Тест успешного просмотра поста"""
        # Настройка моков
        mock_post_instance = Mock()
        mock_post_instance.id = "test-id"
        mock_post_instance.is_private = False
        mock_post_instance.author_id = 123
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        mock_post_view.get_or_create = AsyncMock(return_value=(Mock(), True))
        mock_kafka.send_post_view_event = Mock(return_value=True)
        
        # Создание запроса
        request = posts_pb2.ViewPostRequest(post_id="test-id", user_id=456)
        
        # Выполнение
        response = await self.service.ViewPost(request, self.context)
        
        # Проверки
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Post viewed successfully")
        mock_kafka.send_post_view_event.assert_called_once_with("test-id", 456)
    
    @patch('post_service.app.servicer.Post')
    async def test_view_post_not_found(self, mock_post):
        """Тест просмотра несуществующего поста"""
        mock_post.get_or_none = AsyncMock(return_value=None)
        self.context.abort = AsyncMock()
        
        request = posts_pb2.ViewPostRequest(post_id="nonexistent", user_id=456)
        
        await self.service.ViewPost(request, self.context)
        
        self.context.abort.assert_called_once_with(
            grpc.StatusCode.NOT_FOUND, 
            "Post not found"
        )
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostView')
    async def test_view_private_post_access_denied(self, mock_post_view, mock_post):
        """Тест просмотра приватного поста другим пользователем"""
        mock_post_instance = Mock()
        mock_post_instance.id = "private-post"
        mock_post_instance.is_private = True
        mock_post_instance.author_id = 123
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        self.context.abort = AsyncMock()
        
        request = posts_pb2.ViewPostRequest(post_id="private-post", user_id=456)
        
        await self.service.ViewPost(request, self.context)
        
        self.context.abort.assert_called_once_with(
            grpc.StatusCode.PERMISSION_DENIED,
            "Access denied to private post"
        )
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostLike')
    @patch('post_service.app.servicer.kafka_producer')
    async def test_like_post_success(self, mock_kafka, mock_post_like, mock_post):
        """Тест успешного лайка поста"""
        # Настройка моков
        mock_post_instance = Mock()
        mock_post_instance.id = "test-id"
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        mock_like_instance = Mock()
        mock_post_like.create = AsyncMock(return_value=mock_like_instance)
        mock_post_like.filter.return_value.count = AsyncMock(return_value=5)
        
        mock_kafka.send_post_like_event = Mock(return_value=True)
        
        request = posts_pb2.LikePostRequest(post_id="test-id", user_id=456)
        
        response = await self.service.LikePost(request, self.context)
        
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Post liked successfully")
        self.assertEqual(response.total_likes, 5)
        mock_kafka.send_post_like_event.assert_called_once_with("test-id", 456, "like")
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostLike')
    async def test_like_post_already_liked(self, mock_post_like, mock_post):
        """Тест повторного лайка поста"""
        mock_post_instance = Mock()
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        # Имитируем что лайк уже существует
        from peewee import IntegrityError
        mock_post_like.create = AsyncMock(side_effect=IntegrityError("UNIQUE constraint failed"))
        mock_post_like.filter.return_value.count = AsyncMock(return_value=3)
        
        self.context.abort = AsyncMock()
        
        request = posts_pb2.LikePostRequest(post_id="test-id", user_id=456)
        
        await self.service.LikePost(request, self.context)
        
        self.context.abort.assert_called_once_with(
            grpc.StatusCode.ALREADY_EXISTS,
            "Post already liked by user"
        )
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostLike')
    @patch('post_service.app.servicer.kafka_producer')
    async def test_unlike_post_success(self, mock_kafka, mock_post_like, mock_post):
        """Тест успешного убирания лайка"""
        mock_post_instance = Mock()
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        mock_like_instance = Mock()
        mock_post_like.get_or_none = AsyncMock(return_value=mock_like_instance)
        mock_like_instance.delete_instance = AsyncMock()
        mock_post_like.filter.return_value.count = AsyncMock(return_value=2)
        
        mock_kafka.send_post_like_event = Mock(return_value=True)
        
        request = posts_pb2.UnlikePostRequest(post_id="test-id", user_id=456)
        
        response = await self.service.UnlikePost(request, self.context)
        
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Post unliked successfully")
        self.assertEqual(response.total_likes, 2)
        mock_kafka.send_post_like_event.assert_called_once_with("test-id", 456, "unlike")
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostLike')
    async def test_unlike_post_not_liked(self, mock_post_like, mock_post):
        """Тест убирания несуществующего лайка"""
        mock_post_instance = Mock()
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        mock_post_like.get_or_none = AsyncMock(return_value=None)
        self.context.abort = AsyncMock()
        
        request = posts_pb2.UnlikePostRequest(post_id="test-id", user_id=456)
        
        await self.service.UnlikePost(request, self.context)
        
        self.context.abort.assert_called_once_with(
            grpc.StatusCode.NOT_FOUND,
            "Like not found"
        )
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostComment')
    @patch('post_service.app.servicer.kafka_producer')
    async def test_comment_post_success(self, mock_kafka, mock_post_comment, mock_post):
        """Тест успешного добавления комментария"""
        mock_post_instance = Mock()
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        mock_comment_instance = Mock()
        mock_comment_instance.id = 123
        mock_comment_instance.post_id = "test-id"
        mock_comment_instance.user_id = 456
        mock_comment_instance.content = "Great post!"
        mock_comment_instance.created_at = "2023-01-01T00:00:00Z"
        mock_comment_instance.updated_at = "2023-01-01T00:00:00Z"
        
        mock_post_comment.create = AsyncMock(return_value=mock_comment_instance)
        mock_kafka.send_post_comment_event = Mock(return_value=True)
        
        request = posts_pb2.CommentPostRequest(
            post_id="test-id", 
            user_id=456, 
            content="Great post!"
        )
        
        response = await self.service.CommentPost(request, self.context)
        
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Comment added successfully")
        self.assertEqual(response.comment.content, "Great post!")
        mock_kafka.send_post_comment_event.assert_called_once_with("test-id", 456, 123, "Great post!")
    
    @patch('post_service.app.servicer.Post')
    @patch('post_service.app.servicer.PostComment')
    async def test_get_post_comments_success(self, mock_post_comment, mock_post):
        """Тест получения комментариев с пагинацией"""
        mock_post_instance = Mock()
        mock_post.get_or_none = AsyncMock(return_value=mock_post_instance)
        
        mock_comments = []
        for i in range(3):
            comment = Mock()
            comment.id = i + 1
            comment.post_id = "test-id"
            comment.user_id = 100 + i
            comment.content = f"Comment {i + 1}"
            comment.created_at = "2023-01-01T00:00:00Z"
            comment.updated_at = "2023-01-01T00:00:00Z"
            mock_comments.append(comment)
        
        mock_post_comment.select.return_value.where.return_value.order_by.return_value.paginate = AsyncMock(return_value=mock_comments)
        mock_post_comment.select.return_value.where.return_value.count = AsyncMock(return_value=10)
        
        request = posts_pb2.GetPostCommentsRequest(
            post_id="test-id",
            page=1,
            page_size=5
        )
        
        response = await self.service.GetPostComments(request, self.context)
        
        self.assertEqual(len(response.comments), 3)
        self.assertEqual(response.total_count, 10)
        self.assertEqual(response.page, 1)
        self.assertEqual(response.page_size, 5)
        self.assertEqual(response.comments[0].content, "Comment 1")


if __name__ == '__main__':
    unittest.main() 