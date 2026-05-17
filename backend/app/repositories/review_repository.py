from typing import Optional, List, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_professional(
        self, professional_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Review], int]:
        query = (
            self.db.query(Review)
            .filter(Review.professional_id == professional_id)
            .order_by(Review.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_id(self, review_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_client_and_professional(
        self, client_id: int, professional_id: int
    ) -> Optional[Review]:
        return (
            self.db.query(Review)
            .filter(Review.client_id == client_id, Review.professional_id == professional_id)
            .first()
        )

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_average_rating(self, professional_id: int) -> Tuple[float, int]:
        result = (
            self.db.query(func.avg(Review.rating), func.count(Review.id))
            .filter(Review.professional_id == professional_id)
            .first()
        )
        avg = float(result[0]) if result[0] is not None else 0.0
        count = result[1] if result[1] is not None else 0
        return avg, count
