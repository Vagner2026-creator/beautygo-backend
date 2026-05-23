from app.tests.conftest import register_and_login, auth_header


def _setup(client):
    """Cria admin+categoria e profissional+perfil. Retorna (pro_token, cat_id, pro_id)."""
    admin_token = register_and_login(client, "admin@svc.com", role="admin", name="Admin")
    cat = client.post("/api/v1/categories/", json={"name": "Cabelo"}, headers=auth_header(admin_token))
    cat_id = cat.json()["id"]

    pro_token = register_and_login(client, "pro@svc.com", role="professional", name="Pro")
    pro = client.post("/api/v1/professionals/", json={"business_name": "Studio"}, headers=auth_header(pro_token))
    pro_id = pro.json()["id"]

    return pro_token, cat_id, pro_id


def test_create_service(client):
    pro_token, cat_id, pro_id = _setup(client)

    r = client.post("/api/v1/services/", json={
        "category_id": cat_id,
        "name": "Corte Feminino",
        "duration_minutes": 60,
        "price": "80.00",
    }, headers=auth_header(pro_token))

    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Corte Feminino"
    assert data["duration_minutes"] == 60
    assert float(data["price"]) == 80.0
    assert data["is_active"] is True
    assert data["category"]["name"] == "Cabelo"


def test_create_service_invalid_category(client):
    pro_token, _, _ = _setup(client)
    r = client.post("/api/v1/services/", json={
        "category_id": 99999,
        "name": "Serviço X",
        "duration_minutes": 30,
        "price": "50.00",
    }, headers=auth_header(pro_token))
    assert r.status_code == 404


def test_create_service_not_professional(client):
    admin_token = register_and_login(client, "admin2@svc.com", role="admin", name="Admin2")
    cat = client.post("/api/v1/categories/", json={"name": "Unhas"}, headers=auth_header(admin_token))

    client_token = register_and_login(client, "cli@svc.com", role="client", name="Client")
    r = client.post("/api/v1/services/", json={
        "category_id": cat.json()["id"],
        "name": "Manicure",
        "duration_minutes": 45,
        "price": "40.00",
    }, headers=auth_header(client_token))
    assert r.status_code == 403


def test_list_services(client):
    pro_token, cat_id, pro_id = _setup(client)
    client.post("/api/v1/services/", json={
        "category_id": cat_id, "name": "Hidratação", "duration_minutes": 90, "price": "120.00",
    }, headers=auth_header(pro_token))

    r = client.get(f"/api/v1/services/professionals/{pro_id}/services")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Hidratação"


def test_update_service(client):
    pro_token, cat_id, _ = _setup(client)
    svc = client.post("/api/v1/services/", json={
        "category_id": cat_id, "name": "Escova", "duration_minutes": 45, "price": "60.00",
    }, headers=auth_header(pro_token))
    svc_id = svc.json()["id"]

    r = client.patch(f"/api/v1/services/{svc_id}", json={"price": "70.00", "name": "Escova Premium"},
                     headers=auth_header(pro_token))
    assert r.status_code == 200
    assert float(r.json()["price"]) == 70.0
    assert r.json()["name"] == "Escova Premium"


def test_delete_service(client):
    pro_token, cat_id, pro_id = _setup(client)
    svc = client.post("/api/v1/services/", json={
        "category_id": cat_id, "name": "Tintura", "duration_minutes": 120, "price": "200.00",
    }, headers=auth_header(pro_token))
    svc_id = svc.json()["id"]

    r = client.delete(f"/api/v1/services/{svc_id}", headers=auth_header(pro_token))
    assert r.status_code == 204

    r = client.get(f"/api/v1/services/professionals/{pro_id}/services")
    assert all(s["id"] != svc_id for s in r.json())


def test_delete_service_other_professional(client):
    pro_token, cat_id, _ = _setup(client)
    svc = client.post("/api/v1/services/", json={
        "category_id": cat_id, "name": "Relaxamento", "duration_minutes": 60, "price": "90.00",
    }, headers=auth_header(pro_token))
    svc_id = svc.json()["id"]

    other_token = register_and_login(client, "pro2@svc.com", role="professional", name="Pro2")
    client.post("/api/v1/professionals/", json={"business_name": "Outro Salão"}, headers=auth_header(other_token))

    r = client.delete(f"/api/v1/services/{svc_id}", headers=auth_header(other_token))
    assert r.status_code == 403
