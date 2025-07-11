from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate
from app.services.user import create_user
from app.schemas.auth import Login, Token, ValidateData, TokenRequest, RefreshTokenRequest
from app.services.auth import generate_user_token, generate_user_login, get_user_token, renovate_access_token, get_current_active_user, user_logout, get_public_key

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}}
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user in the system
    """
    db_user = create_user(db, user)
    return {
        "message": "Usario creado exitosamente",
        "username": db_user.username,
        "user_id": db_user.id}

@router.post("/login", response_model=Login, status_code=status.HTTP_200_OK)
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    log in the user and retrieve their athentication token and profile attributes
    """
    access_token , refresh_token, user = generate_user_login(db,form_data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user":user}

@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    get access token and refresh token
    """
    
    access_token , refresh_token = generate_user_token(db, form_data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/validate", response_model=ValidateData, status_code=status.HTTP_200_OK)
async def validate_token(
    token: TokenRequest,
    db: Session = Depends(get_db)
):
    """
    recieves and validates user
    """
    user = get_user_token(db, token)

    return {"user": user}

@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def get_access_token(
    token: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    renovate access token
    """
    access_token , refresh_token = renovate_access_token(db, token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    logout the user and invalidate all refreshtoken associate to the user
    """
    user_logout(db, current_user)

    return {"message": "Logout successful"}

@router.get("/public-key", status_code=status.HTTP_200_OK)
async def public_key():
    pblc_key = get_public_key()

    if not pblc_key:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se encontro la llave pública",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    
    return {"public_key": pblc_key.replace("\n", "")}