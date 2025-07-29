from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class UserBase(BaseModel):
    """ Schema for users"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserUpdate(UserBase):
    is_admin: bool

class UserCreate(UserBase):
    """Schema to create users"""
    password: str = Field(..., min_length=8)

    @field_validator("username")
    def username_aplhanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("El nombre del usuario debe ser alfanumérico")
        return v
    
class UserSelfUpdate(BaseModel):
    """Schema to ge user info"""
    email: EmailStr
    full_name: str
    
class UserInfo(BaseModel):
    """Schema to get user info *Admin only*"""
    id: int 
    username: str
    email: EmailStr
    created_at: datetime

class ProfileUpdateResponse(BaseModel):
    message: str
    user: UserInfo


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class Pagination(BaseModel):
    page: int
    limit: int
    total: int

class UserListResponse(BaseModel):
    users: list[UserInfo]
    pagination: Pagination

