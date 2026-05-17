from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    professional_id: int
    service_id: int
    appointment_date: str  # "YYYY-MM-DD"
    start_time: str        # "HH:MM"
    client_name: str
    client_phone: str
    notes: Optional[str] = None


class AppointmentReschedule(BaseModel):
    appointment_date: str  # "YYYY-MM-DD"
    start_time: str        # "HH:MM"


class AppointmentResponse(BaseModel):
    id: int
    client_id: int
    professional_id: int
    service_id: int
    appointment_date: str
    start_time: str
    end_time: str
    status: str
    client_name: str
    client_phone: str
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
