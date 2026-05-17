from typing import List, Optional
from datetime import datetime, date, time, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.availability import Availability
from app.models.blocked_date import BlockedDate
from app.models.user import User, UserRole
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
    BlockedDateCreate,
    BlockedDateResponse,
)


def _parse_time(time_str: str) -> time:
    """Parse 'HH:MM' string into datetime.time."""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Formato de hora inválido: '{time_str}'. Use HH:MM",
        )


def _parse_date(date_str: str) -> date:
    """Parse 'YYYY-MM-DD' string into datetime.date."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Formato de data inválido: '{date_str}'. Use YYYY-MM-DD",
        )


def _time_to_str(t: time) -> str:
    return t.strftime("%H:%M")


def _date_to_str(d: date) -> str:
    return d.strftime("%Y-%m-%d")


class AvailabilityService:
    def __init__(self, db: Session):
        self.repo = AvailabilityRepository(db)
        self.pro_repo = ProfessionalRepository(db)

    def _get_professional_for_user(self, user: User):
        if user.role not in (UserRole.PROFESSIONAL, UserRole.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        professional = self.pro_repo.get_by_user_id(user.id)
        if not professional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil profissional não encontrado",
            )
        return professional

    # ── Availability CRUD ─────────────────────────────────────────────────────

    def create_availability(self, user: User, data: AvailabilityCreate) -> AvailabilityResponse:
        professional = self._get_professional_for_user(user)

        if not (0 <= data.weekday <= 6):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="weekday deve ser entre 0 (segunda) e 6 (domingo)",
            )

        start = _parse_time(data.start_time)
        end = _parse_time(data.end_time)
        if start >= end:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time deve ser anterior a end_time",
            )

        availability = Availability(
            professional_id=professional.id,
            weekday=data.weekday,
            start_time=start,
            end_time=end,
        )
        created = self.repo.create(availability)
        return _availability_to_response(created)

    def update_availability(
        self, user: User, availability_id: int, data: AvailabilityUpdate
    ) -> AvailabilityResponse:
        professional = self._get_professional_for_user(user)

        avail = self.repo.get_by_id(availability_id)
        if not avail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disponibilidade não encontrada")
        if avail.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        if data.start_time is not None:
            avail.start_time = _parse_time(data.start_time)
        if data.end_time is not None:
            avail.end_time = _parse_time(data.end_time)
        if data.is_active is not None:
            avail.is_active = data.is_active

        if avail.start_time >= avail.end_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time deve ser anterior a end_time",
            )

        updated = self.repo.update(avail)
        return _availability_to_response(updated)

    def delete_availability(self, user: User, availability_id: int) -> None:
        professional = self._get_professional_for_user(user)

        avail = self.repo.get_by_id(availability_id)
        if not avail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disponibilidade não encontrada")
        if avail.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        self.repo.delete(avail)

    def get_professional_availability(self, professional_id: int) -> dict:
        professional = self.pro_repo.get_by_id(professional_id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")

        availabilities = self.repo.list_by_professional(professional_id)
        blocked_dates = self.repo.list_blocked_dates(professional_id)

        return {
            "availability": [_availability_to_response(a) for a in availabilities],
            "blocked_dates": [_blocked_date_to_response(b) for b in blocked_dates],
        }

    # ── Blocked dates ─────────────────────────────────────────────────────────

    def block_date(self, user: User, data: BlockedDateCreate) -> BlockedDateResponse:
        professional = self._get_professional_for_user(user)

        date_val = _parse_date(data.blocked_date)
        existing = self.repo.get_blocked_date(professional.id, date_val)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta data já está bloqueada",
            )

        blocked = BlockedDate(
            professional_id=professional.id,
            blocked_date=date_val,
            reason=data.reason,
        )
        created = self.repo.create_blocked_date(blocked)
        return _blocked_date_to_response(created)

    def unblock_date(self, user: User, blocked_id: int) -> None:
        professional = self._get_professional_for_user(user)

        blocked = self.repo.get_blocked_date_by_id(blocked_id)
        if not blocked:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data bloqueada não encontrada")
        if blocked.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        self.repo.delete_blocked_date(blocked)

    # ── Available slots ───────────────────────────────────────────────────────

    def get_available_slots(
        self,
        professional_id: int,
        date_str: str,
        service_id: int,
        db,
    ) -> List[str]:
        """Return list of available start times 'HH:MM' for the given professional/date/service."""
        from app.repositories.service_repository import ServiceRepository

        professional = self.pro_repo.get_by_id(professional_id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")

        service_repo = ServiceRepository(db)
        service = service_repo.get_by_id(service_id)
        if not service or not service.is_active or service.professional_id != professional_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

        date_val = _parse_date(date_str)

        # Check if date is blocked
        blocked = self.repo.get_blocked_date(professional_id, date_val)
        if blocked:
            return []

        # weekday: Python weekday() → 0=segunda ... 6=domingo  (same convention)
        weekday = date_val.weekday()
        avail = self.repo.get_by_weekday(professional_id, weekday)
        if not avail:
            return []

        duration = timedelta(minutes=int(service.duration_minutes))
        slot_step = timedelta(minutes=30)

        appt_repo = AppointmentRepository(db)

        slots: List[str] = []
        current = datetime.combine(date_val, avail.start_time)
        window_end = datetime.combine(date_val, avail.end_time)

        while current + duration <= window_end:
            slot_start = current.time()
            slot_end = (current + duration).time()

            conflict = appt_repo.check_conflict(professional_id, date_val, slot_start, slot_end)
            if not conflict:
                slots.append(_time_to_str(slot_start))

            current += slot_step

        return slots


# ── Response helpers ─────────────────────────────────────────────────────────

def _availability_to_response(a: Availability) -> AvailabilityResponse:
    return AvailabilityResponse(
        id=a.id,
        professional_id=a.professional_id,
        weekday=a.weekday,
        start_time=_time_to_str(a.start_time),
        end_time=_time_to_str(a.end_time),
        is_active=a.is_active,
    )


def _blocked_date_to_response(b: BlockedDate) -> BlockedDateResponse:
    return BlockedDateResponse(
        id=b.id,
        professional_id=b.professional_id,
        blocked_date=_date_to_str(b.blocked_date),
        reason=b.reason,
    )
