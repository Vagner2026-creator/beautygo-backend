from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter()


@router.get("/professionals/{professional_id}/reviews", response_model=dict)
async def list_reviews(
    professional_id: int,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    return ReviewService(db).list_reviews(professional_id, page=page, size=size)


@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ReviewService(db).create_review(current_user, data)
