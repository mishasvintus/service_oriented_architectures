import os

# gRPC Server Configuration
STATISTICS_PORT = int(os.getenv('STATISTICS_PORT', '50053'))

# ClickHouse Configuration
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'clickhouse')
CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', '9000'))
CLICKHOUSE_DATABASE = os.getenv('CLICKHOUSE_DATABASE', 'analytics')
CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER', 'default')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', '')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', f'statistics_service_{os.getpid()}')

# Kafka Topics
KAFKA_TOPICS = {
    'POST_VIEWS': 'post-views',
    'POST_LIKES': 'post-likes', 
    'POST_COMMENTS': 'post-comments'
}

# ClickHouse Table Names
CLICKHOUSE_TABLES = {
    'POST_VIEWS': 'post_views',
    'POST_LIKES': 'post_likes',
    'POST_COMMENTS': 'post_comments'
} 