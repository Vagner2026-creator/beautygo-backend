from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_admin
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse, UserListResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = 1, size: int = 20,
    _: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return UserService(db).list_users(page=page, size=size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    _: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return UserService(db).get_by_id(user_id)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).update(current_user, data)


@router.delete("/{user_id}", status_code=204)
async def deactivate_user(
    user_id: int,
    admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    UserService(db).deactivate(user_id, admin)
