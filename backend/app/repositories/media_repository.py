from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.professional_media import ProfessionalMedia


class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_professional(self, professional_id: int) -> List[ProfessionalMedia]:
        return (
            self.db.query(ProfessionalMedia)
            .filter(ProfessionalMedia.professional_id == professional_id)
            .order_by(ProfessionalMedia.created_at.desc())
            .all()
        )

    def get_by_id(self, media_id: int) -> Optional[ProfessionalMedia]:
        return self.db.query(ProfessionalMedia).filter(ProfessionalMedia.id == media_id).first()

    def create(self, media: ProfessionalMedia) -> ProfessionalMedia:
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def delete(self, media: ProfessionalMedia) -> None:
        self.db.delete(media)
        self.db.commit()
