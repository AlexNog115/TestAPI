from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class UserBase(BaseModel):
    """ Schema for users"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema to create users"""
    password: str = Field(..., min_length=8)

    @field_validator("username")
    def username_aplhanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("El nombre del usuario debe ser alfanumérico")
        return v