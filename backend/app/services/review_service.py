from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.review import Review
from app.models.user import User
from app.repositories.review_repository import ReviewRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.review import ReviewCreate, ReviewResponse


class ReviewService:
    def __init__(self, db: Session):
        self.repo = ReviewRepository(db)
        self.pro_repo = ProfessionalRepository(db)
        self.client_repo = ClientRepository(db)

    def list_reviews(self, professional_id: int, page: int = 1, size: int = 20) -> dict:
        professional = self.pro_repo.get_by_id(professional_id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")

        skip = (page - 1) * size
        items, total = self.repo.list_by_professional(professional_id, skip=skip, limit=size)
        return {
            "items": [ReviewResponse.model_validate(r) for r in items],
            "total": total,
            "page": page,
            "size": size,
        }

    def create_review(self, user: User, data: ReviewCreate) -> ReviewResponse:
        client = self.client_repo.get_by_user_id(user.id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas clientes podem avaliar profissionais",
            )

        professional = self.pro_repo.get_by_id(data.professional_id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")

        existing = self.repo.get_by_client_and_professional(client.id, data.professional_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Você já avaliou este profissional",
            )

        review = Review(
            client_id=client.id,
            professional_id=data.professional_id,
            rating=data.rating,
            comment=data.comment,
        )
        created = self.repo.create(review)

        # Recalculate and update professional rating
        avg, count = self.repo.get_average_rating(data.professional_id)
        professional.rating = round(avg, 2)
        professional.rating_count = count
        self.pro_repo.update(professional)

        return ReviewResponse.model_validate(created)
