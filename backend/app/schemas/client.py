from typing import Optional
from pydantic import BaseModel


class ClientCreate(BaseModel):
    cpf: Optional[str] = None
    birth_date: Optional[str] = None
    address: Optional[str] = None
    city_id: Optional[int] = None


class ClientUpdate(BaseModel):
    cpf: Optional[str] = None
    birth_date: Optional[str] = None
    address: Optional[str] = None
    city_id: Optional[int] = None


class ClientResponse(BaseModel):
    id: int
    user_id: int
    cpf: Optional[str]
    birth_date: Optional[str]
    address: Optional[str]
    city_id: Optional[int]

    model_config = {"from_attributes": True}
