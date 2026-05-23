from app.tests.conftest import register_and_login, auth_header


def test_create_professional_profile(client):
    token = register_and_login(client, "pro@test.com", role="professional", name="Pro Teste")
    r = client.post("/api/v1/professionals/", json={
        "business_name": "Salão da Ana",
        "specialty": "Cabelo",
        "experience_years": 5,
    }, headers=auth_header(token))
    assert r.status_code == 201
    data = r.json()
    assert data["business_name"] == "Salão da Ana"
    assert data["specialty"] == "Cabelo"
    assert data["is_verified"] is False
    assert "rating" in data


def test_create_professional_requires_auth(client):
    r = client.post("/api/v1/professionals/", json={"business_name": "X"})
    assert r.status_code == 401


def test_create_duplicate_professional(client):
    token = register_and_login(client, "pro2@test.com", role="professional")
    client.post("/api/v1/professionals/", json={"business_name": "Salão A"}, headers=auth_header(token))
    r = client.post("/api/v1/professionals/", json={"business_name": "Salão B"}, headers=auth_header(token))
    assert r.status_code == 409


def test_get_my_profile(client):
    token = register_and_login(client, "pro3@test.com", role="professional")
    client.post("/api/v1/professionals/", json={"business_name": "Meu Salão"}, headers=auth_header(token))

    r = client.get("/api/v1/professionals/me", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["business_name"] == "Meu Salão"


def test_update_profile(client):
    token = register_and_login(client, "pro4@test.com", role="professional")
    client.post("/api/v1/professionals/", json={"business_name": "Salão Original"}, headers=auth_header(token))

    r = client.patch("/api/v1/professionals/me", json={
        "business_name": "Salão Atualizado",
        "is_available": False,
    }, headers=auth_header(token))
    assert r.status_code == 200
    data = r.json()
    assert data["business_name"] == "Salão Atualizado"
    assert data["is_available"] is False


def test_get_profile_by_id(client):
    token = register_and_login(client, "pro5@test.com", role="professional")
    created = client.post("/api/v1/professionals/", json={"business_name": "Por ID"}, headers=auth_header(token))
    pro_id = created.json()["id"]

    r = client.get(f"/api/v1/professionals/{pro_id}")
    assert r.status_code == 200
    assert r.json()["id"] == pro_id


def test_get_profile_by_invalid_id_returns_404(client):
    r = client.get("/api/v1/professionals/99999")
    assert r.status_code == 404


def test_list_professionals(client):
    token = register_and_login(client, "pro6@test.com", role="professional")
    client.post("/api/v1/professionals/", json={"business_name": "Lista Pro"}, headers=auth_header(token))

    r = client.get("/api/v1/professionals/")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1
