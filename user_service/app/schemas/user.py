from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.user import User
import re

class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None  
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value
        
        pattern = re.compile(r"^\+?[1-9]\d{6,14}$") 
        
        if not pattern.match(value):
            raise ValueError("Invalid phone number format. Expected format: +1234567890 or 1234567890")
        
        return value


UserOut = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=("password_hash",)
)