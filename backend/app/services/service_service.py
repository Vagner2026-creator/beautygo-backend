from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.professional_service import ProfessionalService
from app.models.user import User
from app.repositories.service_repository import ServiceRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse


class ServiceService:
    def __init__(self, db: Session):
        self.repo = ServiceRepository(db)
        self.pro_repo = ProfessionalRepository(db)
        self.cat_repo = CategoryRepository(db)

    def _get_professional_for_user(self, user: User):
        professional = self.pro_repo.get_by_user_id(user.id)
        if not professional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil profissional não encontrado",
            )
        return professional

    def list_services(self, professional_id: int) -> List[ServiceResponse]:
        services = self.repo.list_by_professional(professional_id)
        return [ServiceResponse.model_validate(s) for s in services]

    def create_service(self, user: User, data: ServiceCreate) -> ServiceResponse:
        professional = self._get_professional_for_user(user)

        category = self.cat_repo.get_by_id(data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )

        service = ProfessionalService(
            professional_id=professional.id,
            **data.model_dump(),
        )
        created = self.repo.create(service)
        # reload with joined category
        created = self.repo.get_by_id(created.id)
        return ServiceResponse.model_validate(created)

    def update_service(self, user: User, service_id: int, data: ServiceUpdate) -> ServiceResponse:
        professional = self._get_professional_for_user(user)

        service = self.repo.get_by_id(service_id)
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")
        if service.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        if data.category_id is not None:
            category = self.cat_repo.get_by_id(data.category_id)
            if not category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(service, field, value)

        updated = self.repo.update(service)
        return ServiceResponse.model_validate(updated)

    def delete_service(self, user: User, service_id: int) -> None:
        professional = self._get_professional_for_user(user)

        service = self.repo.get_by_id(service_id)
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")
        if service.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        self.repo.delete(service)
