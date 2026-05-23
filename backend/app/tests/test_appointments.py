from datetime import date, timedelta
from app.tests.conftest import register_and_login, auth_header


def _next_weekday(weekday):
    """Retorna a próxima data futura para o dia da semana (0=segunda)."""
    today = date.today()
    days = (weekday - today.weekday()) % 7
    return today + timedelta(days=days if days > 0 else 7)


def _setup(client):
    """
    Setup completo: admin+categoria, profissional+perfil+serviço+disponibilidade, cliente+perfil.
    Retorna (pro_token, client_token, pro_id, svc_id, appt_date_str).
    """
    admin_token = register_and_login(client, "admin@appt.com", role="admin", name="Admin")
    cat = client.post("/api/v1/categories/", json={"name": "Cabelo"}, headers=auth_header(admin_token))
    cat_id = cat.json()["id"]

    pro_token = register_and_login(client, "pro@appt.com", role="professional", name="Pro")
    pro = client.post("/api/v1/professionals/", json={"business_name": "Studio"}, headers=auth_header(pro_token))
    pro_id = pro.json()["id"]

    svc = client.post("/api/v1/services/", json={
        "category_id": cat_id, "name": "Corte", "duration_minutes": 60, "price": "80.00",
    }, headers=auth_header(pro_token))
    svc_id = svc.json()["id"]

    monday = _next_weekday(0)
    client.post("/api/v1/availability/", json={
        "weekday": 0, "start_time": "09:00", "end_time": "18:00",
    }, headers=auth_header(pro_token))

    cli_token = register_and_login(client, "cli@appt.com", role="client", name="Cliente")
    client.post("/api/v1/clients/", json={}, headers=auth_header(cli_token))

    return pro_token, cli_token, pro_id, svc_id, monday.strftime("%Y-%m-%d")


def test_create_appointment(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    r = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id,
        "service_id": svc_id,
        "appointment_date": appt_date,
        "start_time": "10:00",
        "client_name": "Cliente Teste",
        "client_phone": "11999990000",
    }, headers=auth_header(cli_token))

    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "PENDING"
    assert data["professional_id"] == pro_id
    assert data["start_time"] == "10:00"
    assert data["end_time"] == "11:00"


def test_create_appointment_requires_client_profile(client):
    _, _, pro_id, svc_id, appt_date = _setup(client)

    no_profile_token = register_and_login(client, "nocli@appt.com", role="client", name="Sem Perfil")
    r = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id,
        "service_id": svc_id,
        "appointment_date": appt_date,
        "start_time": "10:00",
        "client_name": "X",
        "client_phone": "11999990001",
    }, headers=auth_header(no_profile_token))
    assert r.status_code == 403


def test_create_appointment_past_date(client):
    _, cli_token, pro_id, svc_id, _ = _setup(client)

    past = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    r = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id,
        "service_id": svc_id,
        "appointment_date": past,
        "start_time": "10:00",
        "client_name": "X",
        "client_phone": "11999990002",
    }, headers=auth_header(cli_token))
    assert r.status_code == 422


def test_confirm_appointment(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    appt = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "10:00",
        "client_name": "Cliente", "client_phone": "11999990003",
    }, headers=auth_header(cli_token))
    appt_id = appt.json()["id"]

    r = client.patch(f"/api/v1/appointments/{appt_id}/confirm", headers=auth_header(pro_token))
    assert r.status_code == 200
    assert r.json()["status"] == "CONFIRMED"


def test_confirm_appointment_by_client_forbidden(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    appt = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "10:00",
        "client_name": "Cliente", "client_phone": "11999990004",
    }, headers=auth_header(cli_token))
    appt_id = appt.json()["id"]

    r = client.patch(f"/api/v1/appointments/{appt_id}/confirm", headers=auth_header(cli_token))
    assert r.status_code == 403


def test_cancel_appointment_by_client(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    appt = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "11:00",
        "client_name": "Cliente", "client_phone": "11999990005",
    }, headers=auth_header(cli_token))
    appt_id = appt.json()["id"]

    r = client.patch(f"/api/v1/appointments/{appt_id}/cancel", headers=auth_header(cli_token))
    assert r.status_code == 200
    assert r.json()["status"] == "CANCELED"


def test_cancel_appointment_by_professional(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    appt = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "12:00",
        "client_name": "Cliente", "client_phone": "11999990006",
    }, headers=auth_header(cli_token))
    appt_id = appt.json()["id"]

    r = client.patch(f"/api/v1/appointments/{appt_id}/cancel", headers=auth_header(pro_token))
    assert r.status_code == 200
    assert r.json()["status"] == "CANCELED"


def test_reschedule_appointment(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    appt = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "13:00",
        "client_name": "Cliente", "client_phone": "11999990007",
    }, headers=auth_header(cli_token))
    appt_id = appt.json()["id"]

    next_monday = _next_weekday(0)
    while next_monday.strftime("%Y-%m-%d") == appt_date:
        next_monday += timedelta(days=7)
    new_date = next_monday.strftime("%Y-%m-%d")

    r = client.patch(f"/api/v1/appointments/{appt_id}/reschedule", json={
        "appointment_date": new_date, "start_time": "14:00",
    }, headers=auth_header(cli_token))
    assert r.status_code == 200
    data = r.json()
    assert data["appointment_date"] == new_date
    assert data["start_time"] == "14:00"
    assert data["status"] == "PENDING"


def test_appointment_time_conflict(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "15:00",
        "client_name": "Cliente 1", "client_phone": "11999990008",
    }, headers=auth_header(cli_token))

    r = client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "15:30",
        "client_name": "Cliente 2", "client_phone": "11999990009",
    }, headers=auth_header(cli_token))
    assert r.status_code == 409


def test_list_client_appointments(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "09:00",
        "client_name": "Cliente", "client_phone": "11999990010",
    }, headers=auth_header(cli_token))

    r = client.get("/api/v1/appointments/client", headers=auth_header(cli_token))
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_list_professional_appointments(client):
    pro_token, cli_token, pro_id, svc_id, appt_date = _setup(client)

    client.post("/api/v1/appointments/", json={
        "professional_id": pro_id, "service_id": svc_id,
        "appointment_date": appt_date, "start_time": "09:00",
        "client_name": "Cliente", "client_phone": "11999990011",
    }, headers=auth_header(cli_token))

    r = client.get("/api/v1/appointments/professional", headers=auth_header(pro_token))
    assert r.status_code == 200
    assert r.json()["total"] == 1
