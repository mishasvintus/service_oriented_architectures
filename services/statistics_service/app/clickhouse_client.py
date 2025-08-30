import logging
from typing import List
from datetime import datetime
from clickhouse_driver import Client
from statistics_service.app.config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_DATABASE
from statistics_service.app.models import PostStats, DynamicsPoint, TopPost, TopUser, PostView, PostLike, PostComment

class ClickHouseClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.client = Client(
                host=CLICKHOUSE_HOST,
                port=CLICKHOUSE_PORT,
                database=CLICKHOUSE_DATABASE,
                user='default',
                password=''
            )
            self.logger.info(f"ClickHouse client initialized for database: {CLICKHOUSE_DATABASE} with user: default")
        except Exception as e:
            self.logger.error(f"Failed to initialize ClickHouse client: {e}")
            self.client = None
    
    def insert_post_view(self, post_view: PostView):
        """Вставка события просмотра поста"""
        if not self.client:
            return
        
        try:
            date_obj = datetime.fromisoformat(post_view.date) if isinstance(post_view.date, str) else post_view.date
            
            self.client.execute(
                "INSERT INTO post_views (post_id, user_id, timestamp, date) VALUES",
                [(post_view.post_id, post_view.user_id, post_view.timestamp, date_obj)]
            )
            self.logger.info(f"✅ Inserted post view: {post_view.post_id} by user {post_view.user_id}")
        except Exception as e:
            self.logger.error(f"❌ Failed to insert post view: {e}")
    
    def insert_post_like(self, post_like: PostLike):
        """Вставка события лайка поста"""
        if not self.client:
            return
        
        try:
            date_obj = datetime.fromisoformat(post_like.date) if isinstance(post_like.date, str) else post_like.date
            
            self.client.execute(
                "INSERT INTO post_likes (post_id, user_id, action, timestamp, date) VALUES",
                [(post_like.post_id, post_like.user_id, post_like.action, post_like.timestamp, date_obj)]
            )
            self.logger.info(f"✅ Inserted post like: {post_like.post_id} by user {post_like.user_id} ({post_like.action})")
        except Exception as e:
            self.logger.error(f"❌ Failed to insert post like: {e}")
    
    def insert_post_comment(self, post_comment: PostComment):
        """Вставка события комментария к посту"""
        if not self.client:
            return
        
        try:
            date_obj = datetime.fromisoformat(post_comment.date) if isinstance(post_comment.date, str) else post_comment.date
            
            self.client.execute(
                "INSERT INTO post_comments (post_id, user_id, comment_id, timestamp, date) VALUES",
                [(post_comment.post_id, post_comment.user_id, post_comment.comment_id, post_comment.timestamp, date_obj)]
            )
            self.logger.info(f"✅ Inserted post comment: {post_comment.post_id} by user {post_comment.user_id}")
        except Exception as e:
            self.logger.error(f"❌ Failed to insert post comment: {e}")
    
    def get_post_stats(self, post_id: str) -> PostStats:
        """Получение базовой статистики по посту"""
        if not self.client:
            return PostStats(post_id=post_id, views_count=0, likes_count=0, comments_count=0)
        
        try:
            views_result = self.client.execute(
                "SELECT count() FROM post_views WHERE post_id = %(post_id)s",
                {'post_id': post_id}
            )
            
            views_count = 0
            if isinstance(views_result, list) and views_result:
                try:
                    views_count = views_result[0][0]
                except (IndexError, TypeError):
                    views_count = 0
            
            likes_result = self.client.execute(
                "SELECT countIf(action = 'like') - countIf(action = 'unlike') FROM post_likes WHERE post_id = %(post_id)s",
                {'post_id': post_id}
            )
            
            likes_count = 0
            if isinstance(likes_result, list) and likes_result:
                try:
                    likes_count = likes_result[0][0]
                except (IndexError, TypeError):
                    likes_count = 0
            
            comments_result = self.client.execute(
                "SELECT count() FROM post_comments WHERE post_id = %(post_id)s",
                {'post_id': post_id}
            )
            comments_count = 0
            if isinstance(comments_result, list) and comments_result:
                try:
                    comments_count = comments_result[0][0]
                except (IndexError, TypeError):
                    comments_count = 0
            
            self.logger.info(f"📊 Post stats for {post_id}: views={views_count}, likes={likes_count}, comments={comments_count}")
            
            return PostStats(
                post_id=post_id,
                views_count=views_count,
                likes_count=likes_count,
                comments_count=comments_count
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get post stats: {e}")
            return PostStats(post_id=post_id, views_count=0, likes_count=0, comments_count=0)
    
    def get_post_views_dynamics(self, post_id: str, days: int = 30) -> List[DynamicsPoint]:
        """Получение динамики просмотров по дням"""
        if not self.client:
            return []
        
        try:
            result = self.client.execute(
                """
                SELECT date, sum(views_count) as count
                FROM post_views_daily 
                WHERE post_id = %(post_id)s AND date >= today() - %(days)s
                GROUP BY date
                ORDER BY date
                """,
                {'post_id': post_id, 'days': days}
            )
            
            if isinstance(result, list) and result:
                return [DynamicsPoint(date=str(row[0]), count=row[1]) for row in result]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get views dynamics: {e}")
            return []
    
    def get_top_posts(self, metric: str, limit: int = 10) -> List[TopPost]:
        """Получение топ постов по метрике"""
        if not self.client:
            return []
        
        try:
            if metric == "views":
                result = self.client.execute(
                    f"""
                    SELECT post_id, count() as count
                    FROM post_views
                    GROUP BY post_id
                    ORDER BY count DESC
                    LIMIT {limit}
                    """
                )
            elif metric == "likes":
                result = self.client.execute(
                    f"""
                    SELECT post_id, countIf(action = 'like') - countIf(action = 'unlike') as count
                    FROM post_likes
                    GROUP BY post_id
                    HAVING count > 0
                    ORDER BY count DESC
                    LIMIT {limit}
                    """
                )
            elif metric == "comments":
                result = self.client.execute(
                    f"""
                    SELECT post_id, count() as count
                    FROM post_comments
                    GROUP BY post_id
                    ORDER BY count DESC
                    LIMIT {limit}
                    """
                )
            else:
                return []
            
            if isinstance(result, list) and result:
                return [TopPost(post_id=row[0], count=row[1], title="") for row in result]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get top posts: {e}")
            return []
    
    def get_top_users(self, metric: str, limit: int = 10) -> List[TopUser]:
        """Получение топ пользователей по метрике"""
        if not self.client:
            return []
        
        try:
            if metric == "posts":
                result = self.client.execute(
                    f"""
                    SELECT user_id, count(DISTINCT post_id) as count
                    FROM (
                        SELECT user_id, post_id FROM post_views
                        UNION ALL
                        SELECT user_id, post_id FROM post_likes
                        UNION ALL
                        SELECT user_id, post_id FROM post_comments
                    )
                    GROUP BY user_id
                    ORDER BY count DESC
                    LIMIT {limit}
                    """
                )
            elif metric == "likes":
                result = self.client.execute(
                    f"""
                    SELECT user_id, count() as count
                    FROM post_likes
                    WHERE action = 'like'
                    GROUP BY user_id
                    ORDER BY count DESC
                    LIMIT {limit}
                    """
                )
            elif metric == "comments":
                result = self.client.execute(
                    f"""
                    SELECT user_id, count() as count
                    FROM post_comments
                    GROUP BY user_id
                    ORDER BY count DESC
                    LIMIT {limit}
                    """
                )
            else:
                return []
            
            if isinstance(result, list) and result:
                return [TopUser(user_id=str(row[0]), count=row[1]) for row in result]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get top users: {e}")
            return []


clickhouse_client = ClickHouseClient() 