from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.location_repository import LocationRepository
from app.models.state import State
from app.models.city import City


class LocationService:
    def __init__(self, db: Session):
        self.repo = LocationRepository(db)

    def list_states(self) -> List[State]:
        return self.repo.list_states()

    def list_cities(self, state_id: int) -> List[City]:
        state = self.repo.get_state_by_id(state_id)
        if not state:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado não encontrado")
        return self.repo.list_cities_by_state(state_id)

    def get_city(self, city_id: int) -> City:
        city = self.repo.get_city_by_id(city_id)
        if not city:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cidade não encontrada")
        return city

    def search_cities(self, name: str) -> List[City]:
        return self.repo.search_cities(name)
