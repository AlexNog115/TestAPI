from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class UserBase(BaseModel):
    """Schema for users"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema to create users"""
    password: str = Field(..., min_length=8)
    
    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('El nombre de usuario debe ser alfanumérico')
        return v

class UserUpdate(BaseModel):
    """Schema for updating users"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_admin : Optional[bool] = None

class UserInDB(UserBase):
    """Schema for user in the database"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class User(UserInDB):
    """Schema for returned users in the API"""
    pass

class Login(BaseModel):
    """Schema for access login"""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserInDB

class Token(BaseModel):
    """Schema for access token"""
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None
    scopes: list[str] = []   

class ValidateData(BaseModel):
    """Schema for validate data"""
    user: UserInDB

class TokenRequest(BaseModel):
    """Schema for access refresh token"""
    access_token: str 

class RefreshTokenRequest(BaseModel):
    """Schema for access refresh token"""
    refresh_token: str

class PublicKeyResponse(BaseModel):
    """Schema for public key response"""
    public_key: str