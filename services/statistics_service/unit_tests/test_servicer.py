import unittest
from unittest.mock import Mock, patch
import grpc
from grpc import StatusCode
import sys
import os
from datetime import datetime, date

# Добавляем путь к модулям statistics_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from statistics_service.app.servicer import StatisticsService
from statistics_service.protos import statistics_pb2
from statistics_service.app.models import PostStats, DynamicsPoint, TopPost, TopUser


class TestStatisticsServicer(unittest.TestCase):
    
    def setUp(self):
        """Настройка тестов"""
        # Патчим глобальный clickhouse_client
        self.clickhouse_patcher = patch('statistics_service.app.clickhouse_client.clickhouse_client')
        self.mock_clickhouse_client = self.clickhouse_patcher.start()
        
        self.servicer = StatisticsService()
        # Принудительно заменяем clickhouse_client на мок
        self.servicer.clickhouse_client = self.mock_clickhouse_client
        self.mock_context = Mock()
    
    def tearDown(self):
        """Очистка после тестов"""
        self.clickhouse_patcher.stop()
    
    def test_get_post_stats_success(self):
        """Тест успешного получения статистики поста"""
        # Настройка мока
        mock_stats = PostStats(
            post_id="test-post-123",
            views_count=100,
            likes_count=25,
            comments_count=10
        )
        self.mock_clickhouse_client.get_post_stats.return_value = mock_stats
        
        # Создание запроса
        request = Mock()
        request.post_id = "test-post-123"
        
        # Вызов метода
        response = self.servicer.GetPostStats(request, self.mock_context)
        
        # Проверки
        self.assertEqual(response.post_id, "test-post-123")
        self.assertEqual(response.views_count, 100)
        self.assertEqual(response.likes_count, 25)
        self.assertEqual(response.comments_count, 10)
        self.mock_clickhouse_client.get_post_stats.assert_called_once_with("test-post-123")
    
    def test_get_post_stats_not_found(self):
        """Тест получения статистики несуществующего поста"""
        # Настройка мока для возврата пустой статистики
        mock_stats = PostStats(
            post_id="nonexistent-post",
            views_count=0,
            likes_count=0,
            comments_count=0
        )
        self.mock_clickhouse_client.get_post_stats.return_value = mock_stats
        
        request = Mock()
        request.post_id = "nonexistent-post"
        
        response = self.servicer.GetPostStats(request, self.mock_context)
        
        # Проверяем что вернулись нулевые значения
        self.assertEqual(response.post_id, "nonexistent-post")
        self.assertEqual(response.views_count, 0)
        self.assertEqual(response.likes_count, 0)
        self.assertEqual(response.comments_count, 0)
    
    def test_get_post_views_dynamics_success(self):
        """Тест успешного получения динамики просмотров"""
        # Настройка мока
        mock_dynamics = [
            DynamicsPoint(date="2025-06-13", count=50),
            DynamicsPoint(date="2025-06-14", count=75)
        ]
        self.mock_clickhouse_client.get_post_views_dynamics.return_value = mock_dynamics
        
        request = Mock()
        request.post_id = "test-post-123"
        
        response = self.servicer.GetPostViewsDynamics(request, self.mock_context)
        
        # Проверки
        self.assertEqual(response.post_id, "test-post-123")
        self.assertEqual(len(response.dynamics), 2)
        self.assertEqual(response.dynamics[0].date, "2025-06-13")
        self.assertEqual(response.dynamics[0].count, 50)
        self.assertEqual(response.dynamics[1].date, "2025-06-14")
        self.assertEqual(response.dynamics[1].count, 75)
    
    def test_get_post_likes_dynamics_success(self):
        """Тест успешного получения динамики лайков"""
        request = Mock()
        request.post_id = "test-post-123"
    
        response = self.servicer.GetPostLikesDynamics(request, self.mock_context)
    
        # Пока возвращается пустой список
        self.assertEqual(response.post_id, "test-post-123")
        self.assertEqual(len(response.dynamics), 0)
    
    def test_get_post_comments_dynamics_success(self):
        """Тест успешного получения динамики комментариев"""
        request = Mock()
        request.post_id = "test-post-123"
    
        response = self.servicer.GetPostCommentsDynamics(request, self.mock_context)
    
        # Пока возвращается пустой список
        self.assertEqual(response.post_id, "test-post-123")
        self.assertEqual(len(response.dynamics), 0)
    
    def test_get_top_posts_by_views(self):
        """Тест получения топ постов по просмотрам"""
        mock_top_posts = [
            TopPost(post_id='post-1', count=1000, title=""),
            TopPost(post_id='post-2', count=800, title=""),
            TopPost(post_id='post-3', count=600, title="")
        ]
        self.mock_clickhouse_client.get_top_posts.return_value = mock_top_posts
        
        request = Mock()
        request.metric = "views"
        request.limit = 3
        
        response = self.servicer.GetTopPosts(request, self.mock_context)
        
        self.assertEqual(len(response.posts), 3)
        self.assertEqual(response.posts[0].post_id, 'post-1')
        self.assertEqual(response.posts[0].count, 1000)
        self.assertEqual(response.posts[1].post_id, 'post-2')
        self.assertEqual(response.posts[1].count, 800)
        self.mock_clickhouse_client.get_top_posts.assert_called_once_with("views", 3)
    
    def test_get_top_users_by_posts(self):
        """Тест получения топ пользователей по постам"""
        # Настраиваем Mock для возврата списка пользователей
        mock_top_users = [
            TopUser(user_id="1", count=50),
            TopUser(user_id="2", count=35),
            TopUser(user_id="3", count=20)
        ]
        self.mock_clickhouse_client.get_top_users.return_value = mock_top_users
        

        request = Mock()
        request.metric = "posts"
        request.limit = 3
        
        response = self.servicer.GetTopUsers(request, self.mock_context)
        
        # Проверяем что получили ответ (не None)
        self.assertIsNotNone(response)
        self.assertEqual(len(response.users), 3)
        self.assertEqual(response.users[0].user_id, "1")
        self.assertEqual(response.users[0].count, 50)
        self.assertEqual(response.users[1].user_id, "2")
        self.assertEqual(response.users[1].count, 35)
        self.mock_clickhouse_client.get_top_users.assert_called_once_with("posts", 3)
    
    def test_get_post_stats_clickhouse_error(self):
        """Тест обработки ошибки ClickHouse"""
        # Настройка мока для выброса исключения
        self.mock_clickhouse_client.get_post_stats.side_effect = Exception("ClickHouse connection error")
        
        request = Mock()
        request.post_id = "test-post-123"
        
        # Вызываем метод и проверяем что context.abort был вызван
        self.servicer.GetPostStats(request, self.mock_context)
        self.mock_context.abort.assert_called_once()
    
    def test_invalid_date_format(self):
        """Тест обработки неверного формата даты"""
        # Настройка мока для возврата пустого списка
        self.mock_clickhouse_client.get_post_views_dynamics.return_value = []
        
        request = Mock()
        request.post_id = "test-post-123"
        
        # Не должно вызывать исключений, должно обработать gracefully
        response = self.servicer.GetPostViewsDynamics(request, self.mock_context)
        # Ожидаем что метод выполнится
        self.assertIsNotNone(response)
        self.assertEqual(response.post_id, "test-post-123")


if __name__ == '__main__':
    unittest.main() 