from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate, UserListResponse, UserResponse


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return user

    def update(self, user: User, data: UserUpdate) -> User:
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone is not None:
            user.phone = data.phone
        return self.repo.update(user)

    def deactivate(self, user_id: int, admin: User) -> User:
        user = self.get_by_id(user_id)
        if user.id == admin.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não pode desativar a si mesmo")
        user.is_active = False
        return self.repo.update(user)

    def list_users(self, page: int = 1, size: int = 20) -> UserListResponse:
        skip = (page - 1) * size
        users, total = self.repo.list_all(skip=skip, limit=size)
        return UserListResponse(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
        )
