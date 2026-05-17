from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.professional import Professional
from app.models.user import User
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas.professional import ProfessionalCreate, ProfessionalUpdate, ProfessionalResponse


class ProfessionalService:
    def __init__(self, db: Session):
        self.repo = ProfessionalRepository(db)

    def create_profile(self, user: User, data: ProfessionalCreate) -> Professional:
        existing = self.repo.get_by_user_id(user.id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Perfil profissional já existe")
        professional = Professional(user_id=user.id, **data.model_dump())
        return self.repo.create(professional)

    def get_profile(self, professional_id: int) -> Professional:
        p = self.repo.get_by_id(professional_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")
        return p

    def get_my_profile(self, user: User) -> Professional:
        p = self.repo.get_by_user_id(user.id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil profissional não encontrado")
        return p

    def update_profile(self, user: User, data: ProfessionalUpdate) -> Professional:
        p = self.get_my_profile(user)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(p, field, value)
        return self.repo.update(p)

    def list_professionals(
        self, page: int = 1, size: int = 20,
        city_id: Optional[int] = None, specialty: Optional[str] = None,
        available_only: bool = False
    ):
        skip = (page - 1) * size
        items, total = self.repo.list_all(
            skip=skip, limit=size,
            city_id=city_id, specialty=specialty, available_only=available_only
        )
        return {"items": [ProfessionalResponse.model_validate(i) for i in items], "total": total, "page": page, "size": size}
