from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserUpdateResponse
from app.schemas.user import UserUpdate, UserInfo, UserBase, UserSelfUpdate, ProfileUpdateResponse, PasswordChange, UserListResponse
from app.services.auth import get_current_admin_user, get_current_active_user
from app.services.user import user_id_update, get_user_profile, user_profile_update, user_change_password, get_user_list, get_user_by_id

router = APIRouter(
    prefix="/api/user",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

@router.put("/me", 
            response_model=ProfileUpdateResponse, 
            status_code=status.HTTP_200_OK)
async def update_user_info(
    update_info: UserSelfUpdate,
    current_user = Depends(get_current_active_user),
    db:Session = Depends(get_db),
):
    """
    Permits the user update his username and email
    """
    print("lo que mando: ", update_info)

    user_updated = user_profile_update(update_info, current_user , db)

    return {"message": "Profile updated successfully", "user": user_updated}

@router.put("/{user_id}", response_model = UserUpdateResponse, status_code=status.HTTP_200_OK)
async def update_user_id(
    user_id: int,
    user_update: UserUpdate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    permits admin update information from an especific user with user_id
    """
    user = user_id_update(user_id, db, user_update , current_user)

    return {"message": "User updated successfully", "user": user}

@router.get("/me", response_model= UserInfo, status_code=status.HTTP_200_OK)
async def user_profile(
    user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    get the profile information of the user
    """
    user_info = get_user_profile(user, db)

    return user_info



@router.post("/password/change", status_code=status.HTTP_200_OK)
async def change_password(
    passwords: PasswordChange,
    current_user = Depends(get_current_active_user),
    db:Session = Depends(get_db)
):
    """The User can change his password"""

    user_change_password(passwords, current_user, db)

    return {"message": "Password changed successfully"}

@router.get("/", response_model= UserListResponse,status_code=status.HTTP_200_OK)
async def user_list(
    page: int,
    limit: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    users, total = get_user_list(page, limit, current_user, db)

    return{"users": users, "pagination":{"page": page, "limit": limit, "total": total}}

@router.get("/{user_id}", response_model=UserInfo, status_code=status.HTTP_200_OK)
async def get_user_info(
    user_id: int,
    user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    permits an admin user get a user profile with a user_id
    """
    user_info = get_user_by_id(user_id, db)

    return user_info