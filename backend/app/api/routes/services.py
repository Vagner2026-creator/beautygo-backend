from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_professional
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services.service_service import ServiceService

router = APIRouter()


@router.get("/professionals/{professional_id}/services", response_model=List[ServiceResponse])
async def list_services(professional_id: int, db: Session = Depends(get_db)):
    return ServiceService(db).list_services(professional_id)


@router.post("/", response_model=ServiceResponse, status_code=201)
async def create_service(
    data: ServiceCreate,
    current_user: User = Depends(get_current_professional),
    db: Session = Depends(get_db),
):
    return ServiceService(db).create_service(current_user, data)


@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    data: ServiceUpdate,
    current_user: User = Depends(get_current_professional),
    db: Session = Depends(get_db),
):
    return ServiceService(db).update_service(current_user, service_id, data)


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_professional),
    db: Session = Depends(get_db),
):
    ServiceService(db).delete_service(current_user, service_id)
