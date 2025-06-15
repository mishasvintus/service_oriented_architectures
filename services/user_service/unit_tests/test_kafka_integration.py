import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from user_service.app.kafka_producer import KafkaEventProducer


class TestKafkaIntegration(unittest.TestCase):
    
    def setUp(self):
        with patch('user_service.app.kafka_producer.KafkaProducer') as mock_producer_class:
            self.mock_producer = Mock()
            mock_producer_class.return_value = self.mock_producer
            self.kafka_producer = KafkaEventProducer()
    
    def test_send_user_registration_event(self):
        """Тест отправки события регистрации пользователя"""
        # Настройка мока
        future_mock = Mock()
        future_mock.add_callback = Mock()
        future_mock.add_errback = Mock()
        self.mock_producer.send.return_value = future_mock
        
        registration_date = datetime.now()
        
        # Выполнение
        result = self.kafka_producer.send_user_registration_event(123, registration_date)
        
        # Проверки
        self.assertTrue(result)
        self.mock_producer.send.assert_called_once()
        call_args = self.mock_producer.send.call_args
        
        # Первый аргумент - topic
        self.assertEqual(call_args[0][0], 'user-registrations')
        # Keyword arguments
        self.assertEqual(call_args[1]['key'], 'user:123')
        
        event_data = call_args[1]['value']
        self.assertEqual(event_data['event_type'], 'user_registration')
        self.assertEqual(event_data['user_id'], 123)
        self.assertEqual(event_data['registration_date'], registration_date.isoformat())
        self.assertIn('timestamp', event_data)
    
    def test_producer_initialization_failure(self):
        """Тест обработки ошибки инициализации producer"""
        with patch('user_service.app.kafka_producer.KafkaProducer') as mock_producer_class:
            mock_producer_class.side_effect = Exception("Connection failed")
            
            producer = KafkaEventProducer()
            
            # Producer должен быть None
            self.assertIsNone(producer.producer)
            
            # Отправка события должна вернуть False
            result = producer.send_user_registration_event(123, datetime.now())
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main() 