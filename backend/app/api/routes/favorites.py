from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.favorite import FavoriteResponse
from app.services.favorite_service import FavoriteService

router = APIRouter()


@router.get("/", response_model=List[FavoriteResponse])
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return FavoriteService(db).list_favorites(current_user)


@router.post("/{professional_id}", response_model=FavoriteResponse, status_code=201)
async def add_favorite(
    professional_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return FavoriteService(db).add_favorite(current_user, professional_id)


@router.delete("/{professional_id}", status_code=204)
async def remove_favorite(
    professional_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    FavoriteService(db).remove_favorite(current_user, professional_id)
