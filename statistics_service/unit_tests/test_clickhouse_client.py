import pytest
from unittest.mock import Mock, patch
from statistics_service.app.clickhouse_client import ClickHouseClient
from statistics_service.app.models import PostStats, PostView, PostLike, PostComment


class TestClickHouseClient:
    """Тесты для ClickHouse клиента"""
    
    @pytest.fixture
    def clickhouse_client(self):
        """Фикстура для ClickHouse клиента с мокированным подключением"""
        with patch('statistics_service.app.clickhouse_client.Client') as mock_client:
            client = ClickHouseClient()
            client.client = mock_client
            return client
    
    def test_get_post_stats_empty(self, clickhouse_client):
        """Тест получения статистики для поста без данных"""
        # Мокируем пустые результаты запросов
        clickhouse_client.client.execute.side_effect = [
            [(0,)],  # views
            [(0,)],  # likes
            [(0,)]   # comments
        ]
        
        result = clickhouse_client.get_post_stats("test-post-id")
        
        assert isinstance(result, PostStats)
        assert result.post_id == "test-post-id"
        assert result.views_count == 0
        assert result.likes_count == 0
        assert result.comments_count == 0
    
    def test_get_post_stats_with_data(self, clickhouse_client):
        """Тест получения статистики для поста с данными"""
        # Мокируем результаты с данными
        clickhouse_client.client.execute.side_effect = [
            [(100,)],  # views
            [(25,)],   # likes (net likes)
            [(15,)]    # comments
        ]
        
        result = clickhouse_client.get_post_stats("test-post-id")
        
        assert result.views_count == 100
        assert result.likes_count == 25
        assert result.comments_count == 15
    
    def test_get_post_views_dynamics_empty(self, clickhouse_client):
        """Тест получения динамики просмотров для поста без данных"""
        clickhouse_client.client.execute.return_value = []
        
        result = clickhouse_client.get_post_views_dynamics("test-post-id", 30)
        
        assert result == []
    
    def test_get_top_posts_views(self, clickhouse_client):
        """Тест получения топ постов по просмотрам"""
        # Мокируем результат топ постов
        clickhouse_client.client.execute.return_value = [
            ("post-1", 1000),
            ("post-2", 800),
            ("post-3", 600)
        ]
        
        result = clickhouse_client.get_top_posts("views", 10)
        
        assert len(result) == 3
        assert result[0].post_id == "post-1"
        assert result[0].count == 1000
    
    def test_get_top_users_likes(self, clickhouse_client):
        """Тест получения топ пользователей по лайкам"""
        # Мокируем результат топ пользователей
        clickhouse_client.client.execute.return_value = [
            (123, 500),
            (456, 350),
            (789, 200)
        ]
        
        result = clickhouse_client.get_top_users("likes", 10)
        
        assert len(result) == 3
        assert result[0].user_id == "123" 
        assert result[0].count == 500
    
    def test_insert_post_view(self, clickhouse_client):
        """Тест вставки события просмотра поста"""
        from datetime import datetime
        
        post_view = PostView(
            post_id="test-post",
            user_id=123,
            timestamp=datetime.now(),
            date="2024-01-01"
        )
        
        # Тест что метод выполняется без ошибок
        clickhouse_client.insert_post_view(post_view)
        
        # Проверяем что execute был вызван
        clickhouse_client.client.execute.assert_called_once()
    
    def test_invalid_metric_raises_error(self, clickhouse_client):
        """Тест что неизвестная метрика возвращает пустой список"""
        result = clickhouse_client.get_top_posts("invalid_metric", 10)
        assert result == [] 