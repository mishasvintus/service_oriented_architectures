from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


class PostStatsResponse(BaseModel):
    """Схема ответа для базовой статистики поста"""
    post_id: str = Field(..., description="ID поста")
    views_count: int = Field(..., description="Количество просмотров", ge=0)
    likes_count: int = Field(..., description="Количество лайков", ge=0)  
    comments_count: int = Field(..., description="Количество комментариев", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "post_id": "12345",
                "views_count": 150,
                "likes_count": 25,
                "comments_count": 8
            }
        }


class DynamicsPoint(BaseModel):
    """Точка данных для динамики"""
    date: str = Field(..., description="Дата в формате YYYY-MM-DD")
    count: int = Field(..., description="Количество событий", ge=0)


class PostDynamicsResponse(BaseModel):
    """Схема ответа для динамики статистики поста"""
    post_id: str = Field(..., description="ID поста")
    metric: Literal["views", "likes", "comments"] = Field(..., description="Тип метрики")
    dynamics: List[DynamicsPoint] = Field(..., description="Данные динамики по дням")

    class Config:
        json_schema_extra = {
            "example": {
                "post_id": "12345",
                "metric": "views",
                "dynamics": [
                    {"date": "2024-01-01", "count": 10},
                    {"date": "2024-01-02", "count": 15},
                    {"date": "2024-01-03", "count": 20}
                ]
            }
        }


class TopPost(BaseModel):
    """Схема для топ поста"""
    post_id: str = Field(..., description="ID поста")
    count: int = Field(..., description="Количество по метрике", ge=0)


class TopPostsResponse(BaseModel):
    """Схема ответа для топ постов"""
    metric: Literal["views", "likes", "comments"] = Field(..., description="Метрика сортировки")
    posts: List[TopPost] = Field(..., description="Список топ постов")

    class Config:
        json_schema_extra = {
            "example": {
                "metric": "views",
                "posts": [
                    {"post_id": "12345", "count": 1500},
                    {"post_id": "67890", "count": 1200},
                    {"post_id": "11111", "count": 800}
                ]
            }
        }


class TopUser(BaseModel):
    """Схема для топ пользователя"""
    user_id: str = Field(..., description="ID пользователя")
    count: int = Field(..., description="Количество по метрике", ge=0)


class TopUsersResponse(BaseModel):
    """Схема ответа для топ пользователей"""
    metric: Literal["views", "likes", "comments"] = Field(..., description="Метрика сортировки")
    users: List[TopUser] = Field(..., description="Список топ пользователей")

    class Config:
        json_schema_extra = {
            "example": {
                "metric": "likes",
                "users": [
                    {"user_id": "1", "count": 250},
                    {"user_id": "2", "count": 180},
                    {"user_id": "3", "count": 150}
                ]
            }
        } 