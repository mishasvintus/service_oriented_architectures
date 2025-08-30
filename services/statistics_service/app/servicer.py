import logging
import grpc
from statistics_service.protos import statistics_pb2, statistics_pb2_grpc
from statistics_service.app.clickhouse_client import clickhouse_client


class StatisticsService(statistics_pb2_grpc.StatisticsServiceServicer):
    """gRPC Servicer для Statistics Service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.clickhouse_client = clickhouse_client
    
    def GetPostStats(self, request, context):
        """Получение базовой статистики по посту"""
        try:
            post_stats = self.clickhouse_client.get_post_stats(request.post_id)
            
            return statistics_pb2.GetPostStatsResponse(
                post_id=post_stats.post_id,
                views_count=post_stats.views_count,
                likes_count=post_stats.likes_count,
                comments_count=post_stats.comments_count
            )
            
        except Exception as e:
            self.logger.error(f"Error getting post stats: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetPostViewsDynamics(self, request, context):
        """Получение динамики просмотров по посту"""
        try:
            dynamics = self.clickhouse_client.get_post_views_dynamics(request.post_id, 30)
            
            data_points = [
                statistics_pb2.DynamicsPoint(date=point.date, count=point.count)
                for point in dynamics
            ]
            
            return statistics_pb2.GetPostDynamicsResponse(
                post_id=request.post_id,
                metric="views",
                dynamics=data_points
            )
            
        except Exception as e:
            self.logger.error(f"Error getting views dynamics: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetPostLikesDynamics(self, request, context):
        """Получение динамики лайков по посту"""
        try:
            # Пока возвращаем пустой список, так как нет отдельной таблицы для динамики лайков
            return statistics_pb2.GetPostDynamicsResponse(
                post_id=request.post_id,
                metric="likes",
                dynamics=[]
            )
            
        except Exception as e:
            self.logger.error(f"Error getting likes dynamics: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetPostCommentsDynamics(self, request, context):
        """Получение динамики комментариев по посту"""
        try:
            # Пока возвращаем пустой список, так как нет отдельной таблицы для динамики комментариев
            return statistics_pb2.GetPostDynamicsResponse(
                post_id=request.post_id,
                metric="comments",
                dynamics=[]
            )
            
        except Exception as e:
            self.logger.error(f"Error getting comments dynamics: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetTopPosts(self, request, context):
        """Получение топ 10 постов по метрике"""
        try:
            try:
                if hasattr(request, 'limit') and request.limit is not None:
                    limit = int(request.limit)
                    if limit <= 0:
                        limit = 10
                else:
                    limit = 10
            except (ValueError, TypeError):
                limit = 10
            top_posts = self.clickhouse_client.get_top_posts(request.metric, limit)
            
            posts = [
                statistics_pb2.TopPost(
                    post_id=post.post_id,
                    count=post.count
                )
                for post in top_posts
            ]
            
            return statistics_pb2.GetTopPostsResponse(
                metric=request.metric,
                posts=posts
            )
            
        except Exception as e:
            self.logger.error(f"Error getting top posts: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetTopUsers(self, request, context):
        """Получение топ 10 пользователей по метрике"""
        try:
            try:
                if hasattr(request, 'limit') and request.limit is not None:
                    limit = int(request.limit)
                    if limit <= 0:
                        limit = 10
                else:
                    limit = 10
            except (ValueError, TypeError):
                limit = 10
            top_users = self.clickhouse_client.get_top_users(request.metric, limit)
            
            users = [
                statistics_pb2.TopUser(
                    user_id=user.user_id,
                    count=user.count
                )
                for user in top_users
            ]
            
            return statistics_pb2.GetTopUsersResponse(
                metric=request.metric,
                users=users
            )
            
        except Exception as e:
            self.logger.error(f"Error getting top users: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e)) 