from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}
