from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> List[Category]:
        return self.db.query(Category).filter(Category.is_active == True).order_by(Category.name).all()

    def list_all(self) -> List[Category]:
        return self.db.query(Category).order_by(Category.name).all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name).first()

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        self.db.commit()
        self.db.refresh(category)
        return category
