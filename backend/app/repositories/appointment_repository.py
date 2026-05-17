from typing import Optional, List, Tuple
from datetime import date, time
from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj: Appointment) -> Appointment:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def update(self, obj: Appointment) -> Appointment:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_by_client(
        self, client_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Appointment], int]:
        query = (
            self.db.query(Appointment)
            .filter(Appointment.client_id == client_id)
            .order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def list_by_professional(
        self, professional_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Appointment], int]:
        query = (
            self.db.query(Appointment)
            .filter(Appointment.professional_id == professional_id)
            .order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def check_conflict(
        self,
        professional_id: int,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Return True if there is an overlapping PENDING or CONFIRMED appointment."""
        query = (
            self.db.query(Appointment)
            .filter(
                Appointment.professional_id == professional_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
                # Overlap: NOT (end_time <= :start OR start_time >= :end)
                Appointment.end_time > start_time,
                Appointment.start_time < end_time,
            )
        )
        if exclude_id is not None:
            query = query.filter(Appointment.id != exclude_id)
        return query.first() is not None
