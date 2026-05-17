from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.location import StateResponse, CityResponse, CityWithStateResponse
from app.services.location_service import LocationService

router = APIRouter()


@router.get("/states", response_model=List[StateResponse])
async def list_states(db: Session = Depends(get_db)):
    return LocationService(db).list_states()


@router.get("/states/{state_id}/cities", response_model=List[CityResponse])
async def list_cities(state_id: int, db: Session = Depends(get_db)):
    return LocationService(db).list_cities(state_id)


@router.get("/cities/search", response_model=List[CityWithStateResponse])
async def search_cities(name: str, db: Session = Depends(get_db)):
    return LocationService(db).search_cities(name)


@router.get("/cities/{city_id}", response_model=CityWithStateResponse)
async def get_city(city_id: int, db: Session = Depends(get_db)):
    return LocationService(db).get_city(city_id)
