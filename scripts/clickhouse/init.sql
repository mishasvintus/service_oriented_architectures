-- Инициализация базы данных ClickHouse для Statistics Service

CREATE DATABASE IF NOT EXISTS analytics;

USE analytics;

-- Таблица для просмотров постов
CREATE TABLE IF NOT EXISTS post_views (
    post_id String,
    user_id String,
    timestamp DateTime,
    date Date
) ENGINE = MergeTree()
ORDER BY (post_id, date, timestamp);

-- Таблица для лайков постов  
CREATE TABLE IF NOT EXISTS post_likes (
    post_id String,
    user_id String,
    action String,  -- 'like' или 'unlike'
    timestamp DateTime,
    date Date
) ENGINE = MergeTree()
ORDER BY (post_id, date, timestamp);

-- Таблица для комментариев постов
CREATE TABLE IF NOT EXISTS post_comments (
    post_id String,
    user_id String,
    comment_id String,
    timestamp DateTime,
    date Date  
) ENGINE = MergeTree()
ORDER BY (post_id, date, timestamp);

-- Материализованное представление для ежедневной статистики просмотров
CREATE MATERIALIZED VIEW IF NOT EXISTS post_views_daily
ENGINE = SummingMergeTree()
ORDER BY (post_id, date)
AS SELECT
    post_id,
    date,
    count() as views_count
FROM post_views
GROUP BY post_id, date;

-- Материализованное представление для ежедневной статистики лайков
CREATE MATERIALIZED VIEW IF NOT EXISTS post_likes_daily
ENGINE = SummingMergeTree()  
ORDER BY (post_id, date)
AS SELECT
    post_id,
    date,
    countIf(action = 'like') - countIf(action = 'unlike') as likes_count
FROM post_likes
GROUP BY post_id, date;

-- Материализованное представление для ежедневной статистики комментариев
CREATE MATERIALIZED VIEW IF NOT EXISTS post_comments_daily
ENGINE = SummingMergeTree()
ORDER BY (post_id, date)  
AS SELECT
    post_id,
    date,
    count() as comments_count
FROM post_comments
GROUP BY post_id, date; 