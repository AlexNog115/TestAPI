from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate
from app.services.user import create_user
from app.schemas.auth import Login
from app.services.auth import generate_user_token

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
    access_token , refresh_token, user = generate_user_token(db,form_data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user":user}