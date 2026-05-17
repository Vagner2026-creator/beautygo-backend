from datetime import datetime
from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    id: int
    client_id: int
    professional_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
