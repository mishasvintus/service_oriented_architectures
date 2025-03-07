from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from tortoise.contrib.pydantic import pydantic_model_creator
from user_service.app.models.user import User

class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    email: Optional[EmailStr]
    phone: Optional[str]

UserOut = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=("password_hash",)
)