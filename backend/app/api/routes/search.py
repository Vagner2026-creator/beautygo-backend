from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.search import SearchFilters, SearchResult
from app.services.search_service import SearchService

router = APIRouter()


def _optional_user(db: Session = Depends(get_db)):
    """Returns None — authentication is optional on search endpoints."""
    return None


@router.get("/", response_model=SearchResult)
async def search(
    keyword: Optional[str] = None,
    city_id: Optional[int] = None,
    state_id: Optional[int] = None,
    neighborhood: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    max_distance_km: Optional[float] = None,
    home_service: Optional[bool] = None,
    salon_service: Optional[bool] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    filters = SearchFilters(
        keyword=keyword,
        city_id=city_id,
        state_id=state_id,
        neighborhood=neighborhood,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        max_distance_km=max_distance_km,
        home_service=home_service,
        salon_service=salon_service,
        page=page,
        size=size,
    )

    service = SearchService(db)

    # Log search asynchronously (best-effort, no user context required)
    try:
        service.log_search(user_id=None, keyword=keyword, city_id=city_id)
    except Exception:
        pass

    result = service.search(filters, user_lat=lat, user_lng=lng)
    return result


@router.get("/nearby", response_model=SearchResult)
async def search_nearby(
    lat: float,
    lng: float,
    max_distance_km: float = 10.0,
    category_id: Optional[int] = None,
    home_service: Optional[bool] = None,
    salon_service: Optional[bool] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    if lat is None or lng is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parâmetros 'lat' e 'lng' são obrigatórios para busca por proximidade",
        )

    filters = SearchFilters(
        category_id=category_id,
        max_distance_km=max_distance_km,
        home_service=home_service,
        salon_service=salon_service,
        page=page,
        size=size,
    )

    service = SearchService(db)
    return service.search(filters, user_lat=lat, user_lng=lng)
