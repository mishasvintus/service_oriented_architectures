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
                retry_backoff_ms=1000,
                retries=3
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
            
            future = self.producer.send(topic, value=event_data, key=key)
            
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
            logger.info(f"Event sent to topic {topic}: {event_data}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {e}")
            return False
    
    def _on_send_success(self, record_metadata):
        logger.debug(f"Message sent successfully to topic {record_metadata.topic} "
                    f"partition {record_metadata.partition} offset {record_metadata.offset}")
    
    def _on_send_error(self, excp):
        logger.error(f"Failed to send message: {excp}")
    
    def send_post_view_event(self, post_id: str, user_id: int):
        event_data = {
            'event_type': 'post_view',
            'post_id': post_id,
            'user_id': user_id
        }
        return self.send_event('post-views', event_data, key=f"post:{post_id}")
    
    def send_post_like_event(self, post_id: str, user_id: int, action: str):
        event_data = {
            'event_type': 'post_like',
            'post_id': post_id,
            'user_id': user_id,
            'action': action  # 'like' or 'unlike'
        }
        return self.send_event('post-likes', event_data, key=f"post:{post_id}")
    
    def send_post_comment_event(self, post_id: str, user_id: int, comment_id: int, content: str):
        event_data = {
            'event_type': 'post_comment',
            'post_id': post_id,
            'user_id': user_id,
            'comment_id': comment_id,
            'content': content
        }
        return self.send_event('post-comments', event_data, key=f"post:{post_id}")
    
    def close(self):
        if self.producer:
            self.producer.close()

kafka_producer = KafkaEventProducer() 