from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    professional_id: int
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("A avaliação deve ser entre 1 e 5")
        return v


class ReviewResponse(BaseModel):
    id: int
    client_id: int
    professional_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
