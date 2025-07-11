from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Optional
from passlib.context import CryptContext
from fastapi import HTTPException,status, Depends
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.database import get_db
from app.models.user import User
from app.config import settings
from app.models.refresh_token import RefreshToken
from app.schemas.auth import TokenRequest, RefreshTokenRequest

#OAuth2 configuration
oauth2_scheme  = OAuth2PasswordBearer(tokenUrl = "api/auth/token")

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

def get_public_key():
    """Read the public key from file"""
    try:
        with open(settings.RSA_PUBLIC_KEY_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading public key"
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

def get_user_token(db: Session, token: TokenRequest) -> User:
    try:
        acces_token = token.access_token
        private_key = get_private_key()
        decoded_jwt = jwt.decode(acces_token, private_key, algorithms=settings.ALGORITHM)
        sub = decoded_jwt.get("sub")

        user= db.query(User).filter(User.username == sub).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token no es válido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token no es válido",
                headers={"WWW-Authenticate": "Bearer"},
        )

def renovate_access_token(db:Session , token: RefreshTokenRequest) -> tuple[str, str]:

    refresh_token_request = token.refresh_token

    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token_request,
        RefreshToken.is_active == True                                           
        ).first()

    if not db_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El  refresh token no es valido o no esta activo",
                headers={"WWW-Authenticate": "Bearer"},
            )

    private_key = get_private_key()
    decoded_jwt = jwt.decode(refresh_token_request, private_key, algorithms=settings.ALGORITHM)
    sub = decoded_jwt.get("sub")

    user= db.query(User).filter(User.username == sub).first()

    if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token no es válido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )
    
    db_refresh_token.is_active = False
    

    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return access_token, refresh_token

def get_current_user(db:Session, token: str) -> User:
    
    try:
        private_key = get_private_key()
        decoded_jwt = jwt.decode(token, private_key, algorithms=settings.ALGORITHM)
        username = decoded_jwt.get("sub")

        if not username:
             raise HTTPException(
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  detail="token invalido"
             )

    except JWTError:
         raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="token invalido"
         ) 
    
    user= db.query(User).filter(User.username == username).first()
    
    return user

def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    ) -> User:

    current_user = get_current_user(db,token)

    if not current_user or not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="usuario inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return current_user
    
def user_logout(db: Session, current_user: User):

    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_active == True 
        ).all()
    
    if not refresh_token:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token invalido o no existe",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    for token in refresh_token:
        token.is_active = False
        token.revoked_at = datetime.now(timezone.utc)

    db.commit()
    return