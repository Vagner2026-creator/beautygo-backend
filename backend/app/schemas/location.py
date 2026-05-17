from typing import List, Optional
from pydantic import BaseModel


class StateResponse(BaseModel):
    id: int
    name: str
    uf: str

    model_config = {"from_attributes": True}


class CityResponse(BaseModel):
    id: int
    name: str
    state_id: int

    model_config = {"from_attributes": True}


class CityWithStateResponse(BaseModel):
    id: int
    name: str
    state: StateResponse

    model_config = {"from_attributes": True}
