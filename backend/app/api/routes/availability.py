from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
    BlockedDateCreate,
    BlockedDateResponse,
)
from app.services.availability_service import AvailabilityService

router = APIRouter()


@router.get("/professional/{professional_id}", response_model=dict)
async def get_professional_availability(
    professional_id: int,
    db: Session = Depends(get_db),
):
    return AvailabilityService(db).get_professional_availability(professional_id)


@router.get("/professional/{professional_id}/slots", response_model=List[str])
async def get_available_slots(
    professional_id: int,
    date: str = Query(..., description="Data no formato YYYY-MM-DD"),
    service_id: int = Query(..., description="ID do serviço"),
    db: Session = Depends(get_db),
):
    return AvailabilityService(db).get_available_slots(professional_id, date, service_id)


@router.post("/", response_model=AvailabilityResponse, status_code=201)
async def create_availability(
    data: AvailabilityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AvailabilityService(db).create_availability(current_user, data)


@router.patch("/{availability_id}", response_model=AvailabilityResponse)
async def update_availability(
    availability_id: int,
    data: AvailabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AvailabilityService(db).update_availability(current_user, availability_id, data)


@router.delete("/{availability_id}", status_code=204)
async def delete_availability(
    availability_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AvailabilityService(db).delete_availability(current_user, availability_id)


@router.post("/block-date", response_model=BlockedDateResponse, status_code=201)
async def block_date(
    data: BlockedDateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AvailabilityService(db).block_date(current_user, data)


@router.delete("/block-date/{blocked_id}", status_code=204)
async def unblock_date(
    blocked_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AvailabilityService(db).unblock_date(current_user, blocked_id)
