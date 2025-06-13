from pydantic import BaseModel, Field, field_validator
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

class ViewPostResponse(BaseModel):
    success: bool
    message: str

class LikePostResponse(BaseModel):
    success: bool
    message: str
    total_likes: int

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Comment content cannot be empty")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Comment content cannot be empty or only whitespace')
        return v.strip()

class CommentOut(BaseModel):
    id: int
    post_id: str
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

class CommentResponse(BaseModel):
    success: bool
    message: str
    comment: Optional[CommentOut] = None

class PaginatedCommentsOut(BaseModel):
    comments: List[CommentOut]
    total_count: int
    page: int
    page_size: int 