from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentReschedule, AppointmentResponse
from app.services.appointment_service import AppointmentService

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).create_appointment(current_user, data)


@router.get("/client", response_model=dict)
async def list_client_appointments(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).list_client_appointments(current_user, page=page, size=size)


@router.get("/professional", response_model=dict)
async def list_professional_appointments(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).list_professional_appointments(current_user, page=page, size=size)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).get_appointment(current_user, appointment_id)


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).confirm_appointment(current_user, appointment_id)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).cancel_appointment(current_user, appointment_id)


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: int,
    data: AppointmentReschedule,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).reschedule_appointment(current_user, appointment_id, data)
