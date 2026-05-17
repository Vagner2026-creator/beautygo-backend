from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.favorite import Favorite
from app.models.user import User
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.favorite import FavoriteResponse


class FavoriteService:
    def __init__(self, db: Session):
        self.repo = FavoriteRepository(db)
        self.pro_repo = ProfessionalRepository(db)
        self.client_repo = ClientRepository(db)

    def _get_client(self, user: User):
        client = self.client_repo.get_by_user_id(user.id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas clientes podem gerenciar favoritos",
            )
        return client

    def list_favorites(self, user: User) -> List[FavoriteResponse]:
        client = self._get_client(user)
        favorites = self.repo.list_by_client(client.id)
        return [FavoriteResponse.model_validate(f) for f in favorites]

    def add_favorite(self, user: User, professional_id: int) -> FavoriteResponse:
        client = self._get_client(user)

        professional = self.pro_repo.get_by_id(professional_id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")

        existing = self.repo.get(client.id, professional_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profissional já está nos favoritos",
            )

        favorite = Favorite(client_id=client.id, professional_id=professional_id)
        created = self.repo.create(favorite)
        return FavoriteResponse.model_validate(created)

    def remove_favorite(self, user: User, professional_id: int) -> None:
        client = self._get_client(user)

        favorite = self.repo.get(client.id, professional_id)
        if not favorite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorito não encontrado")

        self.repo.delete(favorite)
