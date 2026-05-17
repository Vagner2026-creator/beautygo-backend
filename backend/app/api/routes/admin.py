from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_admin
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminService

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


@router.get("/users")
async def list_users(
    page: int = 1,
    size: int = 20,
    admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return AdminService(db).list_users(page=page, size=size)


@router.get("/professionals")
async def list_professionals(
    page: int = 1,
    size: int = 20,
    verified_only: bool = False,
    admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return AdminService(db).list_professionals(page=page, size=size, verified_only=verified_only)


@router.patch("/professionals/{professional_id}/verify")
async def verify_professional(
    professional_id: int,
    admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return AdminService(db).verify_professional(admin, professional_id)


@router.patch("/users/{user_id}/block")
async def block_user(
    user_id: int,
    admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return AdminService(db).block_user(admin, user_id)


@router.get("/reports")
async def get_reports(
    admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return AdminService(db).get_reports()
