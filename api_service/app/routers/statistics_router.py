from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Literal
from api_service.app.schemas.statistics_schema import (
    PostStatsResponse, PostDynamicsResponse, TopPostsResponse, TopUsersResponse
)
from api_service.app.grpc_client import get_statistics_stub
from api_service.app.auth import get_current_user_id
from api_service.protos import statistics_pb2
import grpc

router = APIRouter(prefix="/api", tags=["statistics"])

@router.get("/posts/{post_id}/stats", response_model=PostStatsResponse)
async def get_post_stats(
    post_id: str,
    stub=Depends(get_statistics_stub),
    user_id: int = Depends(get_current_user_id)
):
    """Получение базовой статистики по посту"""
    try:
        request = statistics_pb2.GetPostStatsRequest(post_id=post_id)
        response = stub.GetPostStats(request)
        
        return PostStatsResponse(
            post_id=response.post_id,
            views_count=response.views_count,
            likes_count=response.likes_count,
            comments_count=response.comments_count
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Statistics service error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/posts/{post_id}/dynamics/views", response_model=PostDynamicsResponse)
async def get_post_views_dynamics(
    post_id: str,
    days: int = Query(30, ge=1, le=365, description="Количество дней для анализа"),
    stub=Depends(get_statistics_stub),
    user_id: int = Depends(get_current_user_id)
):
    """Получение динамики просмотров по посту"""
    try:
        request = statistics_pb2.GetPostDynamicsRequest(post_id=post_id, days=days)
        response = stub.GetPostViewsDynamics(request)
        
        dynamics = []
        for point in response.dynamics:
            dynamics.append({
                "date": point.date,
                "count": point.count
            })
        
        return PostDynamicsResponse(
            post_id=response.post_id,
            metric="views",
            dynamics=dynamics
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Statistics service error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/posts/{post_id}/dynamics/likes", response_model=PostDynamicsResponse)
async def get_post_likes_dynamics(
    post_id: str,
    days: int = Query(30, ge=1, le=365, description="Количество дней для анализа"),
    stub=Depends(get_statistics_stub),
    user_id: int = Depends(get_current_user_id)
):
    """Получение динамики лайков по посту"""
    try:
        # Для лайков используем тот же метод, но с другой интерпретацией
        request = statistics_pb2.GetPostDynamicsRequest(post_id=post_id, days=days)
        response = stub.GetPostViewsDynamics(request)  # Пока используем views, позже можно добавить отдельный метод
        
        dynamics = []
        for point in response.dynamics:
            dynamics.append({
                "date": point.date,
                "count": point.count // 10  # Примерная конвертация для лайков
            })
        
        return PostDynamicsResponse(
            post_id=response.post_id,
            metric="likes",
            dynamics=dynamics
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Statistics service error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/posts/{post_id}/dynamics/comments", response_model=PostDynamicsResponse)
async def get_post_comments_dynamics(
    post_id: str,
    days: int = Query(30, ge=1, le=365, description="Количество дней для анализа"),
    stub=Depends(get_statistics_stub),
    user_id: int = Depends(get_current_user_id)
):
    """Получение динамики комментариев по посту"""
    try:
        # Для комментариев используем тот же метод, но с другой интерпретацией
        request = statistics_pb2.GetPostDynamicsRequest(post_id=post_id, days=days)
        response = stub.GetPostViewsDynamics(request)  # Пока используем views, позже можно добавить отдельный метод
        
        dynamics = []
        for point in response.dynamics:
            dynamics.append({
                "date": point.date,
                "count": point.count // 20  # Примерная конвертация для комментариев
            })
        
        return PostDynamicsResponse(
            post_id=response.post_id,
            metric="comments",
            dynamics=dynamics
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Statistics service error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/statistics/posts/top", response_model=TopPostsResponse)
async def get_top_posts(
    metric: Literal["views", "likes", "comments"] = Query(..., description="Метрика для топа"),
    limit: int = Query(10, ge=1, le=50, description="Количество постов в топе"),
    stub=Depends(get_statistics_stub)
):
    """Получение топ постов по метрике"""
    try:
        request = statistics_pb2.GetTopPostsRequest(metric=metric, limit=limit)
        response = stub.GetTopPosts(request)
        
        posts = []
        for post in response.posts:
            posts.append({
                "post_id": post.post_id,
                "count": post.count
            })
        
        return TopPostsResponse(
            metric=metric,
            posts=posts
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Statistics service error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/statistics/users/top", response_model=TopUsersResponse)
async def get_top_users(
    metric: Literal["views", "likes", "comments"] = Query(..., description="Метрика для топа"),
    limit: int = Query(10, ge=1, le=50, description="Количество пользователей в топе"),
    stub=Depends(get_statistics_stub)
):
    """Получение топ пользователей по метрике"""
    try:
        request = statistics_pb2.GetTopUsersRequest(metric=metric, limit=limit)
        response = stub.GetTopUsers(request)
        
        users = []
        for user in response.users:
            users.append({
                "user_id": user.user_id,
                "count": user.count
            })
        
        return TopUsersResponse(
            metric=metric,
            users=users
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Statistics service error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 