from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_professional
from app.models.user import User
from app.schemas.professional import ProfessionalCreate, ProfessionalUpdate, ProfessionalResponse
from app.services.professional_service import ProfessionalService

router = APIRouter()


@router.get("/", response_model=dict)
async def list_professionals(
    page: int = 1, size: int = 20,
    city_id: Optional[int] = None,
    specialty: Optional[str] = None,
    available_only: bool = False,
    db: Session = Depends(get_db),
):
    return ProfessionalService(db).list_professionals(
        page=page, size=size, city_id=city_id,
        specialty=specialty, available_only=available_only
    )


@router.post("/", response_model=ProfessionalResponse, status_code=201)
async def create_professional_profile(
    data: ProfessionalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProfessionalService(db).create_profile(current_user, data)


@router.get("/me", response_model=ProfessionalResponse)
async def get_my_professional_profile(
    current_user: User = Depends(get_current_professional),
    db: Session = Depends(get_db),
):
    return ProfessionalService(db).get_my_profile(current_user)


@router.patch("/me", response_model=ProfessionalResponse)
async def update_my_professional_profile(
    data: ProfessionalUpdate,
    current_user: User = Depends(get_current_professional),
    db: Session = Depends(get_db),
):
    return ProfessionalService(db).update_profile(current_user, data)


@router.get("/{professional_id}", response_model=ProfessionalResponse)
async def get_professional(
    professional_id: int,
    db: Session = Depends(get_db),
):
    return ProfessionalService(db).get_profile(professional_id)
