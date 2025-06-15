import json
import logging
from datetime import datetime
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
import os

logger = logging.getLogger(__name__)

class KafkaEventProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda v: str(v).encode('utf-8') if v is not None else b'',
                # Настройки для гарантированной доставки
                acks='all',  # Ждем подтверждения от всех реплик
                retries=5,   # Увеличиваем количество попыток
                retry_backoff_ms=1000,
                max_in_flight_requests_per_connection=1,  # Гарантируем порядок
                enable_idempotence=True,  # Предотвращаем дублирование
                # Настройки буферизации
                batch_size=16384,
                linger_ms=100,  # Ждем 100мс для батчинга
                buffer_memory=33554432,
                # Таймауты
                request_timeout_ms=30000,
                delivery_timeout_ms=120000,
                # Компрессия для эффективности
                compression_type='gzip'
            )
            logger.info(f"Kafka producer initialized with servers: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
    
    def send_event(self, topic: str, event_data: Dict[str, Any], key: str | None = None):
        if not self.producer:
            logger.warning("Kafka producer not initialized. Event not sent.")
            return False
        
        try:
            event_data['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Sending event to topic {topic}: {event_data}")
            
            future = self.producer.send(topic, value=event_data, key=key)
            
            # Ждем подтверждения отправки (синхронно)
            record_metadata = future.get(timeout=30)
            
            logger.info(f"✅ Event sent successfully to topic {topic} partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            logger.error(f"❌ Failed to send event to Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending event to Kafka: {e}")
            return False
        finally:
            # Принудительно отправляем все буферизованные сообщения
            if self.producer:
                self.producer.flush()
    
    def _on_send_success(self, record_metadata):
        logger.debug(f"Message sent successfully to topic {record_metadata.topic} "
                    f"partition {record_metadata.partition} offset {record_metadata.offset}")
    
    def _on_send_error(self, excp):
        logger.error(f"Failed to send message: {excp}")
    
    def send_user_registration_event(self, user_id: int, registration_date: datetime):
        event_data = {
            'event_type': 'user_registration',
            'user_id': user_id,
            'registration_date': registration_date.isoformat()
        }
        logger.info(f"🚀 Preparing to send user registration event for user_id={user_id}")
        result = self.send_event('user-registrations', event_data, key=f"user:{user_id}")
        if result:
            logger.info(f"✅ User registration event sent successfully for user_id={user_id}")
        else:
            logger.error(f"❌ Failed to send user registration event for user_id={user_id}")
        return result
    
    def close(self):
        if self.producer:
            self.producer.flush()  # Отправляем все оставшиеся сообщения
            self.producer.close()

kafka_producer = KafkaEventProducer() 