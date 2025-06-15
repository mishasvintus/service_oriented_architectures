import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from post_service.app.kafka_producer import KafkaEventProducer


class TestKafkaProducer(unittest.TestCase):
    
    def setUp(self):
        with patch('post_service.app.kafka_producer.KafkaProducer') as mock_producer_class:
            self.mock_producer = Mock()
            mock_producer_class.return_value = self.mock_producer
            self.kafka_producer = KafkaEventProducer()
    
    def test_send_post_view_event(self):
        """Тест отправки события просмотра поста"""
        future_mock = Mock()
        future_mock.add_callback = Mock()
        future_mock.add_errback = Mock()
        self.mock_producer.send.return_value = future_mock
        
        result = self.kafka_producer.send_post_view_event("post-123", 456)
        
        self.assertTrue(result)
        self.mock_producer.send.assert_called_once()
        call_args = self.mock_producer.send.call_args
        
        # Первый аргумент - topic
        self.assertEqual(call_args[0][0], 'post-views')
        # Keyword arguments
        self.assertEqual(call_args[1]['key'], 'post:post-123')
        
        event_data = call_args[1]['value']
        self.assertEqual(event_data['event_type'], 'post_view')
        self.assertEqual(event_data['post_id'], 'post-123')
        self.assertEqual(event_data['user_id'], 456)
        self.assertIn('timestamp', event_data)
    
    def test_send_post_like_event(self):
        """Тест отправки события лайка поста"""
        future_mock = Mock()
        future_mock.add_callback = Mock()
        future_mock.add_errback = Mock()
        self.mock_producer.send.return_value = future_mock
        
        result = self.kafka_producer.send_post_like_event("post-123", 456, "like")
        
        self.assertTrue(result)
        self.mock_producer.send.assert_called_once()
        call_args = self.mock_producer.send.call_args
        
        # Первый аргумент - topic
        self.assertEqual(call_args[0][0], 'post-likes')
        # Keyword arguments
        self.assertEqual(call_args[1]['key'], 'post:post-123')
        
        event_data = call_args[1]['value']
        self.assertEqual(event_data['event_type'], 'post_like')
        self.assertEqual(event_data['post_id'], 'post-123')
        self.assertEqual(event_data['user_id'], 456)
        self.assertEqual(event_data['action'], 'like')
        self.assertIn('timestamp', event_data)
    
    def test_send_post_unlike_event(self):
        """Тест отправки события убирания лайка"""
        future_mock = Mock()
        future_mock.add_callback = Mock()
        future_mock.add_errback = Mock()
        self.mock_producer.send.return_value = future_mock
        
        result = self.kafka_producer.send_post_like_event("post-123", 456, "unlike")
        
        self.assertTrue(result)
        call_args = self.mock_producer.send.call_args
        event_data = call_args[1]['value']
        self.assertEqual(event_data['action'], 'unlike')
    
    def test_send_post_comment_event(self):
        """Тест отправки события комментария"""
        future_mock = Mock()
        future_mock.add_callback = Mock()
        future_mock.add_errback = Mock()
        self.mock_producer.send.return_value = future_mock
        
        result = self.kafka_producer.send_post_comment_event("post-123", 456, 789, "Great post!")
        
        self.assertTrue(result)
        self.mock_producer.send.assert_called_once()
        call_args = self.mock_producer.send.call_args
        
        # Первый аргумент - topic
        self.assertEqual(call_args[0][0], 'post-comments')
        # Keyword arguments
        self.assertEqual(call_args[1]['key'], 'post:post-123')
        
        event_data = call_args[1]['value']
        self.assertEqual(event_data['event_type'], 'post_comment')
        self.assertEqual(event_data['post_id'], 'post-123')
        self.assertEqual(event_data['user_id'], 456)
        self.assertEqual(event_data['comment_id'], 789)
        self.assertEqual(event_data['content'], 'Great post!')
        self.assertIn('timestamp', event_data)
    
    def test_producer_initialization_failure(self):
        """Тест обработки ошибки инициализации producer"""
        with patch('post_service.app.kafka_producer.KafkaProducer') as mock_producer_class:
            mock_producer_class.side_effect = Exception("Connection failed")
            
            producer = KafkaEventProducer()
            
            # Producer должен быть None
            self.assertIsNone(producer.producer)
            
            # Отправка событий должна вернуть False
            self.assertFalse(producer.send_post_view_event("post-123", 456))
            self.assertFalse(producer.send_post_like_event("post-123", 456, "like"))
            self.assertFalse(producer.send_post_comment_event("post-123", 456, 789, "test"))
    
    def test_send_failure_handling(self):
        """Тест обработки ошибок при отправке"""
        self.mock_producer.send.side_effect = Exception("Send failed")
        
        result = self.kafka_producer.send_post_view_event("post-123", 456)
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main() 