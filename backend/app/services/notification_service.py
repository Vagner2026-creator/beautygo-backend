from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationResponse


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def create(self, user_id: int, title: str, message: str, type: str) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
        )
        return self.repo.create(notification)

    def list_notifications(self, user: User, page: int = 1, size: int = 20) -> dict:
        skip = (page - 1) * size
        items, total = self.repo.list_by_user(user.id, skip=skip, limit=size)
        return {
            "items": [NotificationResponse.model_validate(n) for n in items],
            "total": total,
            "page": page,
            "size": size,
        }

    def mark_read(self, user: User, notification_id: int) -> NotificationResponse:
        notification = self.repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificação não encontrada")
        if notification.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        updated = self.repo.mark_read(notification)
        return NotificationResponse.model_validate(updated)

    def mark_all_read(self, user: User) -> dict:
        self.repo.mark_all_read(user.id)
        return {"detail": "Todas as notificações foram marcadas como lidas"}
