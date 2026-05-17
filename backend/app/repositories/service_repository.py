from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.professional_service import ProfessionalService


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_professional(self, professional_id: int) -> List[ProfessionalService]:
        return (
            self.db.query(ProfessionalService)
            .options(joinedload(ProfessionalService.category))
            .filter(ProfessionalService.professional_id == professional_id)
            .filter(ProfessionalService.is_active == True)
            .order_by(ProfessionalService.name)
            .all()
        )

    def list_all_by_professional(self, professional_id: int) -> List[ProfessionalService]:
        return (
            self.db.query(ProfessionalService)
            .options(joinedload(ProfessionalService.category))
            .filter(ProfessionalService.professional_id == professional_id)
            .order_by(ProfessionalService.name)
            .all()
        )

    def get_by_id(self, service_id: int) -> Optional[ProfessionalService]:
        return (
            self.db.query(ProfessionalService)
            .options(joinedload(ProfessionalService.category))
            .filter(ProfessionalService.id == service_id)
            .first()
        )

    def create(self, service: ProfessionalService) -> ProfessionalService:
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def update(self, service: ProfessionalService) -> ProfessionalService:
        self.db.commit()
        self.db.refresh(service)
        return service

    def delete(self, service: ProfessionalService) -> None:
        self.db.delete(service)
        self.db.commit()
