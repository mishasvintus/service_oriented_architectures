from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PostView:
    """Модель для события просмотра поста"""
    post_id: str
    user_id: str
    timestamp: datetime
    date: str  # YYYY-MM-DD format

@dataclass
class PostLike:
    """Модель для события лайка/дизлайка поста"""
    post_id: str
    user_id: str
    action: str  # 'like' или 'unlike'
    timestamp: datetime
    date: str  # YYYY-MM-DD format

@dataclass
class PostComment:
    """Модель для события комментария к посту"""
    post_id: str
    user_id: str
    comment_id: str
    timestamp: datetime
    date: str  # YYYY-MM-DD format

@dataclass
class PostStats:
    """Модель для статистики поста"""
    post_id: str
    views_count: int
    likes_count: int
    comments_count: int

@dataclass
class DynamicsPoint:
    """Точка данных для динамики"""
    date: str
    count: int

@dataclass
class TopPost:
    """Модель для топ поста"""
    post_id: str
    count: int
    title: Optional[str] = None

@dataclass
class TopUser:
    """Модель для топ пользователя"""
    user_id: str
    count: int 