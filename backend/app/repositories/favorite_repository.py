from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.favorite import Favorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_client(self, client_id: int) -> List[Favorite]:
        return (
            self.db.query(Favorite)
            .filter(Favorite.client_id == client_id)
            .order_by(Favorite.created_at.desc())
            .all()
        )

    def get(self, client_id: int, professional_id: int) -> Optional[Favorite]:
        return (
            self.db.query(Favorite)
            .filter(Favorite.client_id == client_id, Favorite.professional_id == professional_id)
            .first()
        )

    def create(self, favorite: Favorite) -> Favorite:
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def delete(self, favorite: Favorite) -> None:
        self.db.delete(favorite)
        self.db.commit()
