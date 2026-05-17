from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.professional import Professional


class ProfessionalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, professional_id: int) -> Optional[Professional]:
        return self.db.query(Professional).filter(Professional.id == professional_id).first()

    def get_by_user_id(self, user_id: int) -> Optional[Professional]:
        return self.db.query(Professional).filter(Professional.user_id == user_id).first()

    def list_all(
        self, skip: int = 0, limit: int = 20,
        city_id: Optional[int] = None, specialty: Optional[str] = None,
        available_only: bool = False
    ) -> tuple[List[Professional], int]:
        query = self.db.query(Professional).options(joinedload(Professional.user))
        if city_id:
            query = query.filter(Professional.city_id == city_id)
        if specialty:
            query = query.filter(Professional.specialty.ilike(f"%{specialty}%"))
        if available_only:
            query = query.filter(Professional.is_available == True)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, professional: Professional) -> Professional:
        self.db.add(professional)
        self.db.commit()
        self.db.refresh(professional)
        return professional

    def update(self, professional: Professional) -> Professional:
        self.db.commit()
        self.db.refresh(professional)
        return professional
