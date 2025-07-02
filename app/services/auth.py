from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from passlib.context import CryptContext
from fastapi import HTTPException,status
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.models.user import User
from app.config import settings
from app.models.refresh_token import RefreshToken

#configuring bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(passsword: str) -> str:
    """generates a hash for the password"""
    return pwd_context.hash(passsword)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the plaintext password matches the hash"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db:Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by verifying theier username and password"""
    user= db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_private_key():
    """Read the private key from file"""
    try:
        with open(settings.RSA_PRIVATE_KEY_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading private key"
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with the provided data"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    private_key = get_private_key()
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def generate_and_store_tokens(
    db: Session,
    user: User,
    access_token_expires: timedelta,
    refresh_token_expires: timedelta
) -> tuple[str, str]:
    """
    Generate access and refresh tokens for a user and store the refresh token in the database.
    """
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )

    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return access_token, refresh_token

def generate_user_login(db: Session, form_data: OAuth2PasswordRequestForm) -> tuple[str, str, User]:
    """
    Authenticate a user and generate access and refresh token and user information
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
    
    access_token, refresh_token = generate_and_store_tokens(
        db, user, access_token_expires, refresh_token_expires
    )

    return access_token, refresh_token, user

def generate_user_token(db: Session, form_data: OAuth2PasswordRequestForm) -> tuple[str, str]:
    """
    Authenticate a user and generate access and refresh token
    """

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)

    access_token, refresh_token = generate_and_store_tokens(
        db, user, access_token_expires, refresh_token_expires
    )

    return access_token, refresh_token