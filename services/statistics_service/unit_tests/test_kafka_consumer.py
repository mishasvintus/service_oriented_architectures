import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
from datetime import datetime
import sys
import os

# Добавляем путь к модулям statistics_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from statistics_service.app.kafka_consumer import KafkaConsumerService
from statistics_service.app.models import PostView, PostLike, PostComment


class TestKafkaConsumerService(unittest.TestCase):
    
    def setUp(self):
        """Настройка тестов"""
        # Патчим глобальный clickhouse_client ДО создания consumer
        self.clickhouse_patcher = patch('statistics_service.app.clickhouse_client.clickhouse_client')
        self.mock_clickhouse_client = self.clickhouse_patcher.start()
        
        # Создаем consumer после патчинга
        self.consumer = KafkaConsumerService()
        # Принудительно заменяем clickhouse_client на мок
        self.consumer.clickhouse_client = self.mock_clickhouse_client
        
    def tearDown(self):
        """Очистка после тестов"""
        self.clickhouse_patcher.stop()
    
    def test_consumer_initialization(self):
        """Тест инициализации Kafka consumer"""
        self.assertIsNotNone(self.consumer)
        self.assertIsNotNone(self.consumer.clickhouse_client)
    
    def test_process_post_view_event(self):
        """Тест обработки события просмотра поста"""
        event_data = {
            'post_id': 'test-post-123',
            'user_id': 1,
            'timestamp': '2025-06-14T15:30:00'
        }
        
        self.consumer.process_post_view(event_data)
        
        # Проверяем что вызван метод вставки в ClickHouse
        self.mock_clickhouse_client.insert_post_view.assert_called_once()
        call_args = self.mock_clickhouse_client.insert_post_view.call_args[0][0]
        
        self.assertIsInstance(call_args, PostView)
        self.assertEqual(call_args.post_id, 'test-post-123')
        self.assertEqual(call_args.user_id, '1')
    
    def test_process_post_like_event(self):
        """Тест обработки события лайка поста"""
        event_data = {
            'post_id': 'test-post-123',
            'user_id': 1,
            'action': 'like',
            'timestamp': '2025-06-14T15:30:00'
        }
        
        self.consumer.process_post_like(event_data)
        
        # Проверяем что вызван метод вставки в ClickHouse
        self.mock_clickhouse_client.insert_post_like.assert_called_once()
        call_args = self.mock_clickhouse_client.insert_post_like.call_args[0][0]
        
        self.assertIsInstance(call_args, PostLike)
        self.assertEqual(call_args.post_id, 'test-post-123')
        self.assertEqual(call_args.action, 'like')
    
    def test_process_post_comment_event(self):
        """Тест обработки события комментария к посту"""
        event_data = {
            'post_id': 'test-post-123',
            'user_id': 1,
            'comment_id': 42,
            'timestamp': '2025-06-14T15:30:00'
        }
        
        self.consumer.process_post_comment(event_data)
        
        # Проверяем что вызван метод вставки в ClickHouse
        self.mock_clickhouse_client.insert_post_comment.assert_called_once()
        call_args = self.mock_clickhouse_client.insert_post_comment.call_args[0][0]
        
        self.assertIsInstance(call_args, PostComment)
        self.assertEqual(call_args.post_id, 'test-post-123')
        self.assertEqual(call_args.comment_id, '42')
    
    def test_process_message_post_view(self):
        """Тест обработки сообщения с событием просмотра"""
        message = Mock()
        message.topic = 'post-views'
        message.value = {
            'post_id': 'test-post-123',
            'user_id': 1,
            'timestamp': '2025-06-14T15:30:00'
        }
        
        self.consumer.process_message(message)
        
        # Проверяем что был вызван метод обработки просмотра
        self.mock_clickhouse_client.insert_post_view.assert_called_once()
    
    def test_process_message_invalid_data(self):
        """Тест обработки сообщения с невалидными данными"""
        message = Mock()
        message.topic = 'post-views'
        message.value = {
            'post_id': 'test-post-123'
            # Отсутствуют обязательные поля
        }
        
        # Не должно вызывать исключений
        try:
            self.consumer.process_message(message)
        except Exception as e:
            self.fail(f"Обработка невалидного сообщения вызвала исключение: {e}")


if __name__ == '__main__':
    unittest.main() 