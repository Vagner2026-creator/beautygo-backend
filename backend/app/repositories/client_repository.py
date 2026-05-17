from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.client import Client


class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_by_user_id(self, user_id: int) -> Optional[Client]:
        return self.db.query(Client).filter(Client.user_id == user_id).first()

    def get_by_cpf(self, cpf: str) -> Optional[Client]:
        return self.db.query(Client).filter(Client.cpf == cpf).first()

    def list_all(self, skip: int = 0, limit: int = 20) -> tuple[List[Client], int]:
        query = self.db.query(Client).options(joinedload(Client.user))
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, client: Client) -> Client:
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update(self, client: Client) -> Client:
        self.db.commit()
        self.db.refresh(client)
        return client
