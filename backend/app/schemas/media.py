from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class MediaResponse(BaseModel):
    id: int
    professional_id: int
    type: str
    file_url: str
    thumbnail_url: Optional[str]
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
