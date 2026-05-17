from typing import Optional
from pydantic import BaseModel


class AvailabilityCreate(BaseModel):
    weekday: int  # 0-6 (0=segunda, 6=domingo)
    start_time: str  # "HH:MM"
    end_time: str    # "HH:MM"


class AvailabilityUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_active: Optional[bool] = None


class AvailabilityResponse(BaseModel):
    id: int
    professional_id: int
    weekday: int
    start_time: str
    end_time: str
    is_active: bool

    model_config = {"from_attributes": True}


class BlockedDateCreate(BaseModel):
    blocked_date: str  # "YYYY-MM-DD"
    reason: Optional[str] = None


class BlockedDateResponse(BaseModel):
    id: int
    professional_id: int
    blocked_date: str
    reason: Optional[str]

    model_config = {"from_attributes": True}
