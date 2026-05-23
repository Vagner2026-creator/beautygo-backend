from app.tests.conftest import register_and_login, auth_header


def test_create_client_profile(client):
    token = register_and_login(client, "client@test.com", role="client", name="Cliente Teste")
    r = client.post("/api/v1/clients/", json={
        "birth_date": "1990-05-15",
        "address": "Rua das Flores, 123",
    }, headers=auth_header(token))
    assert r.status_code == 201
    data = r.json()
    assert data["birth_date"] == "1990-05-15"
    assert data["address"] == "Rua das Flores, 123"


def test_create_client_requires_auth(client):
    r = client.post("/api/v1/clients/", json={})
    assert r.status_code == 401


def test_get_client_profile(client):
    token = register_and_login(client, "client2@test.com")
    client.post("/api/v1/clients/", json={"address": "Av. Brasil, 500"}, headers=auth_header(token))

    r = client.get("/api/v1/clients/me", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["address"] == "Av. Brasil, 500"


def test_update_client_profile(client):
    token = register_and_login(client, "client3@test.com")
    client.post("/api/v1/clients/", json={}, headers=auth_header(token))

    r = client.patch("/api/v1/clients/me", json={"address": "Nova Rua, 999"}, headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["address"] == "Nova Rua, 999"


def test_create_duplicate_client(client):
    token = register_and_login(client, "client4@test.com")
    client.post("/api/v1/clients/", json={}, headers=auth_header(token))
    r = client.post("/api/v1/clients/", json={}, headers=auth_header(token))
    assert r.status_code == 409


def test_get_profile_without_creating_returns_404(client):
    token = register_and_login(client, "client5@test.com")
    r = client.get("/api/v1/clients/me", headers=auth_header(token))
    assert r.status_code == 404
