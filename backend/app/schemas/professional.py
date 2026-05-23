from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class ProfessionalCreate(BaseModel):
    business_name: str
    description: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: int = 0
    address: Optional[str] = None
    city_id: Optional[int] = None


class ProfessionalUpdate(BaseModel):
    business_name: Optional[str] = None
    description: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    address: Optional[str] = None
    city_id: Optional[int] = None
    is_available: Optional[bool] = None
    profile_image_url: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    neighborhood: Optional[str] = None
    home_service: Optional[bool] = None
    salon_service: Optional[bool] = None


class ProfessionalResponse(BaseModel):
    id: int
    user_id: int
    business_name: str
    description: Optional[str]
    specialty: Optional[str]
    experience_years: int
    rating: Decimal
    rating_count: int
    is_available: bool
    is_verified: bool
    address: Optional[str]
    city_id: Optional[int]
    profile_image_url: Optional[str]
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    neighborhood: Optional[str] = None
    home_service: Optional[bool] = False
    salon_service: Optional[bool] = True

    model_config = {"from_attributes": True}
