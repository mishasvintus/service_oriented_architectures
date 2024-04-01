from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PostCreate(BaseModel):
    title: str
    description: str
    is_private: bool = False
    tags: Optional[List[str]] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    tags: Optional[List[str]] = None

class PostOut(BaseModel):
    id: str
    title: str
    description: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    is_private: bool
    tags: List[str]

class PaginatedPostOut(BaseModel):
    posts: List[PostOut]
    total_count: int
    page: int
    page_size: int 