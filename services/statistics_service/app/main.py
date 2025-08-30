import logging
import grpc
import threading
from concurrent import futures
from statistics_service.app.config import STATISTICS_PORT, CLICKHOUSE_HOST
from statistics_service.protos import statistics_pb2_grpc
from statistics_service.app.servicer import StatisticsService
from statistics_service.app.clickhouse_client import clickhouse_client
from statistics_service.app.kafka_consumer import KafkaConsumerService

def init_clickhouse():
    """Инициализация ClickHouse и создание таблиц"""
    if not clickhouse_client.client:
        logging.error("❌ ClickHouse client is not available")
        return
        
    try:
        clickhouse_client.client.execute("""
            CREATE TABLE IF NOT EXISTS post_views (
                post_id String,
                user_id String,
                timestamp DateTime,
                date Date
            ) ENGINE = MergeTree()
            ORDER BY (post_id, timestamp)
        """)
        
        clickhouse_client.client.execute("""
            CREATE TABLE IF NOT EXISTS post_likes (
                post_id String,
                user_id String,
                action String,
                timestamp DateTime,
                date Date
            ) ENGINE = MergeTree()
            ORDER BY (post_id, timestamp)
        """)
        
        clickhouse_client.client.execute("""
            CREATE TABLE IF NOT EXISTS post_comments (
                post_id String,
                user_id String,
                comment_id String,
                timestamp DateTime,
                date Date
            ) ENGINE = MergeTree()
            ORDER BY (post_id, timestamp)
        """)
        
        logging.info("✅ ClickHouse tables initialized successfully")
    except Exception as e:
        logging.error(f"❌ Failed to initialize ClickHouse tables: {e}")

def start_kafka_consumer():
    """Запуск Kafka Consumer в отдельном потоке"""
    def run_consumer():
        kafka_consumer = KafkaConsumerService()
        kafka_consumer.start_consuming()
    
    kafka_thread = threading.Thread(target=run_consumer, daemon=True)
    kafka_thread.start()
    logging.info("Kafka consumer started in background")

def grpc_server():
    """Запуск gRPC сервера"""
    logging.basicConfig(level=logging.INFO)
    
    init_clickhouse()
    
    start_kafka_consumer()
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    statistics_pb2_grpc.add_StatisticsServiceServicer_to_server(StatisticsService(), server)
    
    listen_addr = f'[::]:{STATISTICS_PORT}'
    server.add_insecure_port(listen_addr)
    
    logging.info(f"Starting Statistics gRPC server on port {STATISTICS_PORT}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    grpc_server() 