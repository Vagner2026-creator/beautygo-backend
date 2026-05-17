from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from app.models.availability import Availability
from app.models.blocked_date import BlockedDate


class AvailabilityRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── Availability ──────────────────────────────────────────────────────────

    def list_by_professional(self, professional_id: int) -> List[Availability]:
        return (
            self.db.query(Availability)
            .filter(Availability.professional_id == professional_id)
            .order_by(Availability.weekday, Availability.start_time)
            .all()
        )

    def get_by_id(self, availability_id: int) -> Optional[Availability]:
        return self.db.query(Availability).filter(Availability.id == availability_id).first()

    def get_by_weekday(self, professional_id: int, weekday: int) -> Optional[Availability]:
        return (
            self.db.query(Availability)
            .filter(
                Availability.professional_id == professional_id,
                Availability.weekday == weekday,
                Availability.is_active == True,
            )
            .first()
        )

    def create(self, obj: Availability) -> Availability:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: Availability) -> Availability:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: Availability) -> None:
        self.db.delete(obj)
        self.db.commit()

    # ── BlockedDate ───────────────────────────────────────────────────────────

    def list_blocked_dates(self, professional_id: int) -> List[BlockedDate]:
        return (
            self.db.query(BlockedDate)
            .filter(BlockedDate.professional_id == professional_id)
            .order_by(BlockedDate.blocked_date)
            .all()
        )

    def get_blocked_date(self, professional_id: int, date_val: date) -> Optional[BlockedDate]:
        return (
            self.db.query(BlockedDate)
            .filter(
                BlockedDate.professional_id == professional_id,
                BlockedDate.blocked_date == date_val,
            )
            .first()
        )

    def get_blocked_date_by_id(self, blocked_id: int) -> Optional[BlockedDate]:
        return self.db.query(BlockedDate).filter(BlockedDate.id == blocked_id).first()

    def create_blocked_date(self, obj: BlockedDate) -> BlockedDate:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_blocked_date(self, obj: BlockedDate) -> None:
        self.db.delete(obj)
        self.db.commit()
