from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def list_categories(self) -> List[CategoryResponse]:
        categories = self.repo.list_active()
        return [CategoryResponse.model_validate(c) for c in categories]

    def list_all_categories(self) -> List[CategoryResponse]:
        categories = self.repo.list_all()
        return [CategoryResponse.model_validate(c) for c in categories]

    def create_category(self, data: CategoryCreate) -> CategoryResponse:
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Categoria com esse nome já existe",
            )
        category = Category(name=data.name, icon=data.icon)
        created = self.repo.create(category)
        return CategoryResponse.model_validate(created)

    def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(category, field, value)
        updated = self.repo.update(category)
        return CategoryResponse.model_validate(updated)
