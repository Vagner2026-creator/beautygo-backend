from typing import Optional, List, Any
from pydantic import BaseModel


class SearchFilters(BaseModel):
    keyword: Optional[str] = None
    city_id: Optional[int] = None
    state_id: Optional[int] = None
    neighborhood: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    max_distance_km: Optional[float] = None
    home_service: Optional[bool] = None
    salon_service: Optional[bool] = None
    page: int = 1
    size: int = 20


class SearchResult(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
