import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from statistics_service.app.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP, KAFKA_TOPICS
from statistics_service.app.models import PostView, PostLike, PostComment
from statistics_service.app.clickhouse_client import clickhouse_client


class KafkaConsumerService:
    """Kafka Consumer для обработки событий"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clickhouse_client = clickhouse_client
        self.consumer = None
    
    def parse_timestamp(self, timestamp_str):
        """Парсинг timestamp из различных форматов"""
        try:
            if timestamp_str.endswith('Z'):
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif '+' in timestamp_str or timestamp_str.endswith('+00:00'):
                return datetime.fromisoformat(timestamp_str)
            else:

                return datetime.fromisoformat(timestamp_str)
        except Exception as e:
            self.logger.error(f"Failed to parse timestamp '{timestamp_str}': {e}")

            return datetime.now()
    
    def start_consuming(self):
        """Запуск потребления событий из Kafka"""
        try:
            self.logger.info("🔄 Initializing Kafka consumer...")
            
            self.consumer = KafkaConsumer(
                KAFKA_TOPICS['POST_VIEWS'],
                KAFKA_TOPICS['POST_LIKES'],
                KAFKA_TOPICS['POST_COMMENTS'],
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                group_id=KAFKA_CONSUMER_GROUP,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            
            self.logger.info("✅ Kafka consumer initialized, starting to consume messages...")
            
            for message in self.consumer:
                try:
                    self.process_message(message)
                except Exception as e:
                    self.logger.error(f"❌ Error processing message: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Kafka consumer error: {e}")
            
    def process_message(self, message):
        """Обработка одного сообщения"""
        topic = message.topic
        event_data = message.value
        
        self.logger.info(f"📨 Processing message from topic {topic}: {event_data}")
        
        try:
            if topic == KAFKA_TOPICS['POST_VIEWS']:
                self.process_post_view(event_data)
            elif topic == KAFKA_TOPICS['POST_LIKES']:
                self.process_post_like(event_data)
            elif topic == KAFKA_TOPICS['POST_COMMENTS']:
                self.process_post_comment(event_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing {topic} event: {e}")
            
    def process_post_view(self, event_data):
        """Обработка события просмотра поста"""
        try:
            timestamp = self.parse_timestamp(event_data['timestamp'])
            
            post_view = PostView(
                post_id=event_data['post_id'],
                user_id=str(event_data['user_id']),
                timestamp=timestamp,
                date=timestamp.date().isoformat()
            )
            
            self.clickhouse_client.insert_post_view(post_view)
            self.logger.info(f"✅ Processed post view: {post_view.post_id} by user {post_view.user_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing post view: {e}")
            
    def process_post_like(self, event_data):
        """Обработка события лайка поста"""
        try:
            timestamp = self.parse_timestamp(event_data['timestamp'])
            
            post_like = PostLike(
                post_id=event_data['post_id'],
                user_id=str(event_data['user_id']),
                action=event_data.get('action', 'like'),  # like или unlike
                timestamp=timestamp,
                date=timestamp.date().isoformat()
            )
            
            self.clickhouse_client.insert_post_like(post_like)
            self.logger.info(f"✅ Processed post like: {post_like.post_id} by user {post_like.user_id} ({post_like.action})")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing post like: {e}")
            
    def process_post_comment(self, event_data):
        """Обработка события комментария к посту"""
        try:
            timestamp = self.parse_timestamp(event_data['timestamp'])
            
            post_comment = PostComment(
                post_id=event_data['post_id'],
                user_id=str(event_data['user_id']),
                comment_id=str(event_data['comment_id']),
                timestamp=timestamp,
                date=timestamp.date().isoformat()
            )
            
            self.clickhouse_client.insert_post_comment(post_comment)
            self.logger.info(f"✅ Processed post comment: {post_comment.post_id} by user {post_comment.user_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing post comment: {e}") 