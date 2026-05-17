from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.state import State
from app.models.city import City


class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_states(self) -> List[State]:
        return self.db.query(State).order_by(State.name).all()

    def get_state_by_uf(self, uf: str) -> Optional[State]:
        return self.db.query(State).filter(State.uf == uf.upper()).first()

    def list_cities_by_state(self, state_id: int) -> List[City]:
        return (
            self.db.query(City)
            .filter(City.state_id == state_id)
            .order_by(City.name)
            .all()
        )

    def get_city_by_id(self, city_id: int) -> Optional[City]:
        return (
            self.db.query(City)
            .options(joinedload(City.state))
            .filter(City.id == city_id)
            .first()
        )

    def search_cities(self, name: str) -> List[City]:
        return (
            self.db.query(City)
            .options(joinedload(City.state))
            .filter(City.name.ilike(f"%{name}%"))
            .limit(20)
            .all()
        )
