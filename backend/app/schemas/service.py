from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from app.schemas.category import CategoryResponse


class ServiceCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price: Decimal


class ServiceUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ServiceResponse(BaseModel):
    id: int
    professional_id: int
    category_id: int
    name: str
    description: Optional[str]
    duration_minutes: int
    price: Decimal
    is_active: bool
    created_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = {"from_attributes": True}
