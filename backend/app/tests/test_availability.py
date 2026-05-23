from datetime import date, timedelta
from app.tests.conftest import register_and_login, auth_header


def _setup_professional(client):
    """Cria profissional com perfil. Retorna (token, pro_id)."""
    token = register_and_login(client, "pro@avail.com", role="professional", name="Pro")
    r = client.post("/api/v1/professionals/", json={"business_name": "Studio"}, headers=auth_header(token))
    return token, r.json()["id"]


def _next_monday():
    today = date.today()
    days = (0 - today.weekday()) % 7
    return today + timedelta(days=days if days > 0 else 7)


def test_create_availability(client):
    token, pro_id = _setup_professional(client)

    r = client.post("/api/v1/availability/", json={
        "weekday": 1,
        "start_time": "09:00",
        "end_time": "18:00",
    }, headers=auth_header(token))
    assert r.status_code == 201
    data = r.json()
    assert data["weekday"] == 1
    assert data["start_time"] == "09:00"
    assert data["end_time"] == "18:00"
    assert data["is_active"] is True


def test_create_availability_invalid_weekday(client):
    token, _ = _setup_professional(client)
    r = client.post("/api/v1/availability/", json={
        "weekday": 9, "start_time": "09:00", "end_time": "18:00",
    }, headers=auth_header(token))
    assert r.status_code == 422


def test_create_availability_invalid_times(client):
    token, _ = _setup_professional(client)
    r = client.post("/api/v1/availability/", json={
        "weekday": 2, "start_time": "18:00", "end_time": "09:00",
    }, headers=auth_header(token))
    assert r.status_code == 422


def test_create_availability_requires_professional(client):
    token = register_and_login(client, "cli@avail.com", role="client")
    r = client.post("/api/v1/availability/", json={
        "weekday": 0, "start_time": "09:00", "end_time": "17:00",
    }, headers=auth_header(token))
    assert r.status_code == 403


def test_get_professional_availability(client):
    token, pro_id = _setup_professional(client)
    client.post("/api/v1/availability/", json={
        "weekday": 0, "start_time": "08:00", "end_time": "12:00",
    }, headers=auth_header(token))

    r = client.get(f"/api/v1/availability/professional/{pro_id}")
    assert r.status_code == 200
    data = r.json()
    assert "availability" in data
    assert "blocked_dates" in data
    assert len(data["availability"]) == 1


def test_update_availability(client):
    token, _ = _setup_professional(client)
    created = client.post("/api/v1/availability/", json={
        "weekday": 3, "start_time": "09:00", "end_time": "17:00",
    }, headers=auth_header(token))
    avail_id = created.json()["id"]

    r = client.patch(f"/api/v1/availability/{avail_id}", json={"end_time": "18:00"},
                     headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["end_time"] == "18:00"


def test_delete_availability(client):
    token, pro_id = _setup_professional(client)
    created = client.post("/api/v1/availability/", json={
        "weekday": 5, "start_time": "10:00", "end_time": "16:00",
    }, headers=auth_header(token))
    avail_id = created.json()["id"]

    r = client.delete(f"/api/v1/availability/{avail_id}", headers=auth_header(token))
    assert r.status_code == 204

    data = client.get(f"/api/v1/availability/professional/{pro_id}").json()
    assert all(a["id"] != avail_id for a in data["availability"])


def test_block_date(client):
    token, pro_id = _setup_professional(client)
    future = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")

    r = client.post("/api/v1/availability/block-date", json={
        "blocked_date": future, "reason": "Férias",
    }, headers=auth_header(token))
    assert r.status_code == 201
    assert r.json()["blocked_date"] == future
    assert r.json()["reason"] == "Férias"


def test_block_duplicate_date(client):
    token, _ = _setup_professional(client)
    future = (date.today() + timedelta(days=15)).strftime("%Y-%m-%d")

    client.post("/api/v1/availability/block-date", json={"blocked_date": future}, headers=auth_header(token))
    r = client.post("/api/v1/availability/block-date", json={"blocked_date": future}, headers=auth_header(token))
    assert r.status_code == 409


def test_unblock_date(client):
    token, pro_id = _setup_professional(client)
    future = (date.today() + timedelta(days=20)).strftime("%Y-%m-%d")

    blocked = client.post("/api/v1/availability/block-date", json={"blocked_date": future},
                          headers=auth_header(token))
    blocked_id = blocked.json()["id"]

    r = client.delete(f"/api/v1/availability/block-date/{blocked_id}", headers=auth_header(token))
    assert r.status_code == 204

    data = client.get(f"/api/v1/availability/professional/{pro_id}").json()
    assert all(b["id"] != blocked_id for b in data["blocked_dates"])


def test_get_available_slots(client):
    admin_token = register_and_login(client, "admin@avail.com", role="admin", name="Admin")
    cat = client.post("/api/v1/categories/", json={"name": "Cabelo"}, headers=auth_header(admin_token))
    cat_id = cat.json()["id"]

    pro_token = register_and_login(client, "pro2@avail.com", role="professional", name="Pro2")
    pro = client.post("/api/v1/professionals/", json={"business_name": "Studio2"}, headers=auth_header(pro_token))
    pro_id = pro.json()["id"]

    monday = _next_monday()
    client.post("/api/v1/availability/", json={
        "weekday": monday.weekday(),
        "start_time": "09:00",
        "end_time": "12:00",
    }, headers=auth_header(pro_token))

    svc = client.post("/api/v1/services/", json={
        "category_id": cat_id, "name": "Corte", "duration_minutes": 60, "price": "50.00",
    }, headers=auth_header(pro_token))
    svc_id = svc.json()["id"]

    r = client.get(f"/api/v1/availability/professional/{pro_id}/slots",
                   params={"date": monday.strftime("%Y-%m-%d"), "service_id": svc_id})
    assert r.status_code == 200
    slots = r.json()
    assert isinstance(slots, list)
    assert "09:00" in slots
