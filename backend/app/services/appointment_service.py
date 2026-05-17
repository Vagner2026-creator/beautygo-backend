from datetime import datetime, date, time, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.appointment import AppointmentCreate, AppointmentReschedule, AppointmentResponse
from app.services.notification_service import NotificationService


def _parse_time(time_str: str) -> time:
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Formato de hora inválido: '{time_str}'. Use HH:MM",
        )


def _parse_date(date_str: str) -> date:
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


def _appointment_to_response(a: Appointment) -> AppointmentResponse:
    return AppointmentResponse(
        id=a.id,
        client_id=a.client_id,
        professional_id=a.professional_id,
        service_id=a.service_id,
        appointment_date=_date_to_str(a.appointment_date),
        start_time=_time_to_str(a.start_time),
        end_time=_time_to_str(a.end_time),
        status=a.status.value,
        client_name=a.client_name,
        client_phone=a.client_phone,
        notes=a.notes,
        created_at=a.created_at,
    )


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AppointmentRepository(db)
        self.avail_repo = AvailabilityRepository(db)
        self.client_repo = ClientRepository(db)
        self.pro_repo = ProfessionalRepository(db)
        self.service_repo = ServiceRepository(db)
        self.notif_service = NotificationService(db)

    def _validate_slot(
        self,
        professional_id: int,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_id: Optional[int] = None,
    ) -> None:
        """Shared validation: date not past, not blocked, within availability window, no conflict."""
        today = datetime.now(timezone.utc).date()
        if appointment_date < today:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Não é possível agendar em uma data passada",
            )

        # Check blocked date
        blocked = self.avail_repo.get_blocked_date(professional_id, appointment_date)
        if blocked:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O profissional não está disponível nesta data",
            )

        # Check availability window (weekday)
        weekday = appointment_date.weekday()
        avail = self.avail_repo.get_by_weekday(professional_id, weekday)
        if not avail:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O profissional não atende neste dia da semana",
            )
        if start_time < avail.start_time or end_time > avail.end_time:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Horário fora do período de atendimento ({_time_to_str(avail.start_time)} - {_time_to_str(avail.end_time)})",
            )

        # Check time conflict
        conflict = self.repo.check_conflict(
            professional_id, appointment_date, start_time, end_time, exclude_id=exclude_id
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um agendamento neste horário",
            )

    # ── Create ────────────────────────────────────────────────────────────────

    def create_appointment(self, user: User, data: AppointmentCreate) -> AppointmentResponse:
        client = self.client_repo.get_by_user_id(user.id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas clientes podem criar agendamentos",
            )

        professional = self.pro_repo.get_by_id(data.professional_id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado")

        service = self.service_repo.get_by_id(data.service_id)
        if not service or not service.is_active or service.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

        appointment_date = _parse_date(data.appointment_date)
        start_time = _parse_time(data.start_time)
        end_time = (datetime.combine(appointment_date, start_time) + timedelta(minutes=int(service.duration_minutes))).time()

        self._validate_slot(professional.id, appointment_date, start_time, end_time)

        appointment = Appointment(
            client_id=client.id,
            professional_id=professional.id,
            service_id=service.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            status=AppointmentStatus.PENDING,
            client_name=data.client_name,
            client_phone=data.client_phone,
            notes=data.notes,
        )
        created = self.repo.create(appointment)

        # Notify professional
        self.notif_service.create(
            user_id=professional.user_id,
            title="Novo agendamento",
            message=f"{data.client_name} agendou {service.name} para {data.appointment_date} às {data.start_time}.",
            type="appointment_new",
        )

        return _appointment_to_response(created)

    # ── Confirm ───────────────────────────────────────────────────────────────

    def confirm_appointment(self, user: User, appointment_id: int) -> AppointmentResponse:
        appointment = self.repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

        professional = self.pro_repo.get_by_user_id(user.id)
        if not professional or appointment.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        if appointment.status != AppointmentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Apenas agendamentos pendentes podem ser confirmados",
            )

        appointment.status = AppointmentStatus.CONFIRMED
        updated = self.repo.update(appointment)

        # Notify client
        self.notif_service.create(
            user_id=appointment.client.user_id,
            title="Agendamento confirmado",
            message=f"Seu agendamento para {_date_to_str(appointment.appointment_date)} às {_time_to_str(appointment.start_time)} foi confirmado.",
            type="appointment_confirmed",
        )

        return _appointment_to_response(updated)

    # ── Cancel ────────────────────────────────────────────────────────────────

    def cancel_appointment(self, user: User, appointment_id: int) -> AppointmentResponse:
        appointment = self.repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

        is_client = (
            appointment.client.user_id == user.id
        )
        professional = self.pro_repo.get_by_user_id(user.id)
        is_professional = professional and appointment.professional_id == professional.id

        if not is_client and not is_professional:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        if appointment.status not in (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Apenas agendamentos pendentes ou confirmados podem ser cancelados",
            )

        appointment.status = AppointmentStatus.CANCELED
        updated = self.repo.update(appointment)

        # Notify the other party
        if is_client:
            # Notify professional
            self.notif_service.create(
                user_id=appointment.professional.user_id,
                title="Agendamento cancelado",
                message=f"O cliente cancelou o agendamento de {_date_to_str(appointment.appointment_date)} às {_time_to_str(appointment.start_time)}.",
                type="appointment_canceled",
            )
        else:
            # Notify client
            self.notif_service.create(
                user_id=appointment.client.user_id,
                title="Agendamento cancelado",
                message=f"Seu agendamento de {_date_to_str(appointment.appointment_date)} às {_time_to_str(appointment.start_time)} foi cancelado pelo profissional.",
                type="appointment_canceled",
            )

        return _appointment_to_response(updated)

    # ── Reschedule ────────────────────────────────────────────────────────────

    def reschedule_appointment(
        self, user: User, appointment_id: int, data: AppointmentReschedule
    ) -> AppointmentResponse:
        appointment = self.repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

        if appointment.client.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o cliente pode reagendar o agendamento",
            )

        if appointment.status not in (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Apenas agendamentos pendentes ou confirmados podem ser reagendados",
            )

        new_date = _parse_date(data.appointment_date)
        new_start = _parse_time(data.start_time)

        service = self.service_repo.get_by_id(appointment.service_id)
        new_end = (datetime.combine(new_date, new_start) + timedelta(minutes=int(service.duration_minutes))).time()

        self._validate_slot(
            appointment.professional_id, new_date, new_start, new_end, exclude_id=appointment.id
        )

        appointment.appointment_date = new_date
        appointment.start_time = new_start
        appointment.end_time = new_end
        appointment.status = AppointmentStatus.PENDING  # reset to pending on reschedule
        updated = self.repo.update(appointment)

        # Notify professional
        self.notif_service.create(
            user_id=appointment.professional.user_id,
            title="Agendamento reagendado",
            message=f"O cliente reagendou para {data.appointment_date} às {data.start_time}.",
            type="appointment_rescheduled",
        )

        return _appointment_to_response(updated)

    # ── List & Get ────────────────────────────────────────────────────────────

    def list_client_appointments(self, user: User, page: int = 1, size: int = 20) -> dict:
        client = self.client_repo.get_by_user_id(user.id)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de cliente não encontrado")
        skip = (page - 1) * size
        items, total = self.repo.list_by_client(client.id, skip=skip, limit=size)
        return {
            "items": [_appointment_to_response(a) for a in items],
            "total": total,
            "page": page,
            "size": size,
        }

    def list_professional_appointments(self, user: User, page: int = 1, size: int = 20) -> dict:
        professional = self.pro_repo.get_by_user_id(user.id)
        if not professional:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil profissional não encontrado")
        skip = (page - 1) * size
        items, total = self.repo.list_by_professional(professional.id, skip=skip, limit=size)
        return {
            "items": [_appointment_to_response(a) for a in items],
            "total": total,
            "page": page,
            "size": size,
        }

    def get_appointment(self, user: User, appointment_id: int) -> AppointmentResponse:
        appointment = self.repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

        is_client = appointment.client.user_id == user.id
        professional = self.pro_repo.get_by_user_id(user.id)
        is_professional = professional and appointment.professional_id == professional.id
        is_admin = user.role == UserRole.ADMIN

        if not (is_client or is_professional or is_admin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        return _appointment_to_response(appointment)
