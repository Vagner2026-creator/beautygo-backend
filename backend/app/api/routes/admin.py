from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_admin
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.get("/stats")
async def get_stats(
    _: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    return {
        "total_users": repo.count_by_role(UserRole.CLIENT) + repo.count_by_role(UserRole.PROFESSIONAL),
        "total_clients": repo.count_by_role(UserRole.CLIENT),
        "total_professionals": repo.count_by_role(UserRole.PROFESSIONAL),
        "total_admins": repo.count_by_role(UserRole.ADMIN),
    }
