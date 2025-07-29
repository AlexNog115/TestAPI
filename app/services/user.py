from sqlalchemy.orm import Session
from sqlalchemy import update
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordChange, UserSelfUpdate
from app.services.auth import get_password_hash, verify_password

def get_user_by_email(db:Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db:Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    #Check if the email is already registered
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El coreo electrónico ya esta registrado"
        )

    #Check if the username is already registered
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usario ya esta registrado"
        )

    #Create the user object with the hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def user_profile_update(user_update: UserSelfUpdate, current_user: User, db: Session):
    
    email_exists = db.query(User).filter(
        User.email == user_update.email,
        User.id != current_user.id
        ).first()

    if not email_exists and user_update.email == email_exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El email ya existe"
        )
    
    update_values = update(User).where(User.id == current_user.id).values(full_name = user_update.full_name, email = user_update.email)
    db.execute(update_values)
    db.commit()
    db.refresh(current_user)

    return current_user

def user_id_update(user_id: int, db: Session, user_update: UserUpdate, current_user: User):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="usuario no encontrado"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede modificar el propio usuario"
        )

    email_exists = db.query(User).filter(
        User.email == user_update.email,
        User.id != user.id
        ).first()

    if not email_exists and user_update.email == email_exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El email ya existe"
        )
    
    username_exists = db.query(User).filter(User.username == user_update.username, User.id != user.id).first()

    if not username_exists and username_exists == user_update.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="nombre de usuario ya en uso"
        )

    user.username = user_update.username
    user.email = user_update.email
    user.full_name = user_update.full_name
    user.is_admin = user_update.is_admin
    db.commit()
    db.refresh(user)

    return user

def get_user_profile(user: User, db:Session):

    user_info = db.query(User).filter(User.id == user.id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="id de usuario inválido")
    
    return user_info

def get_user_by_id(user_id: int, db:Session):

    user_info = db.query(User).filter(User.id == user_id).first()

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="id de usuario inválido")
    
    return user_info


def user_change_password(passwords: PasswordChange, current_user: User, db:Session):


    if not verify_password(passwords.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es incorrecta")
    
    if passwords.current_password == passwords.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña tiene que ser diferente a la anterior"
        )
    
    current_user.hashed_password = get_password_hash(passwords.new_password)
    db.add(current_user)
    db.commit()

    return

def get_user_list(page: int, limit: int, current_user:User, db:Session):

    skip_page = (page - 1)* limit
    total = db.query(User).count()
    users = db.query(User).offset(skip_page).limit(limit).all()

    return users, total
    