from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.models.admin_log import AdminLog
from app.models.appointment import AppointmentStatus
from app.repositories.user_repository import UserRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.client_repository import ClientRepository


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.pro_repo = ProfessionalRepository(db)
        self.client_repo = ClientRepository(db)

    def _log(self, admin: User, action: str, target_type: str, target_id=None, description=None):
        log = AdminLog(
            admin_id=admin.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
        )
        self.db.add(log)
        self.db.commit()

    def list_users(self, page: int = 1, size: int = 20) -> dict:
        skip = (page - 1) * size
        items, total = self.user_repo.list_all(skip=skip, limit=size)
        return {
            "items": [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "role": u.role.value,
                    "is_active": u.is_active,
                    "is_verified": u.is_verified,
                    "created_at": u.created_at,
                }
                for u in items
            ],
            "total": total,
            "page": page,
            "size": size,
        }

    def list_professionals(self, page: int = 1, size: int = 20, verified_only: bool = False) -> dict:
        from app.models.professional import Professional

        skip = (page - 1) * size
        query = self.db.query(Professional)
        if verified_only:
            query = query.filter(Professional.is_verified == True)
        total = query.count()
        items = query.offset(skip).limit(size).all()
        return {
            "items": [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "business_name": p.business_name,
                    "specialty": p.specialty,
                    "is_verified": p.is_verified,
                    "is_available": p.is_available,
                    "rating": float(p.rating) if p.rating is not None else 0.0,
                    "rating_count": p.rating_count,
                    "created_at": p.created_at,
                }
                for p in items
            ],
            "total": total,
            "page": page,
            "size": size,
        }

    def verify_professional(self, admin: User, professional_id: int) -> dict:
        professional = self.pro_repo.get_by_id(professional_id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")

        professional.is_verified = True
        self.pro_repo.update(professional)

        self._log(
            admin,
            action="verify_professional",
            target_type="professional",
            target_id=professional_id,
            description=f"Profissional {professional.business_name} verificado",
        )

        return {"detail": "Profissional verificado com sucesso", "professional_id": professional_id}

    def block_user(self, admin: User, user_id: int) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é possível bloquear outro administrador",
            )

        user.is_active = False
        self.user_repo.update(user)

        self._log(
            admin,
            action="block_user",
            target_type="user",
            target_id=user_id,
            description=f"Usuário {user.email} bloqueado",
        )

        return {"detail": "Usuário bloqueado com sucesso", "user_id": user_id}

    def get_reports(self) -> dict:
        from app.models.appointment import Appointment
        from app.models.client import Client
        from app.models.professional import Professional

        total_users = self.user_repo.count_by_role(UserRole.CLIENT) + self.user_repo.count_by_role(UserRole.PROFESSIONAL)
        total_clients = self.db.query(Client).count()
        total_professionals = self.db.query(Professional).count()

        total_appointments = self.db.query(Appointment).count()
        total_pending = self.db.query(Appointment).filter(Appointment.status == AppointmentStatus.PENDING).count()
        total_confirmed = self.db.query(Appointment).filter(Appointment.status == AppointmentStatus.CONFIRMED).count()
        total_canceled = self.db.query(Appointment).filter(Appointment.status == AppointmentStatus.CANCELED).count()
        total_completed = self.db.query(Appointment).filter(Appointment.status == AppointmentStatus.COMPLETED).count()

        return {
            "total_users": total_users,
            "total_clients": total_clients,
            "total_professionals": total_professionals,
            "total_appointments": total_appointments,
            "total_pending": total_pending,
            "total_confirmed": total_confirmed,
            "total_canceled": total_canceled,
            "total_completed": total_completed,
        }
