from app.tests.conftest import register_and_login, auth_header


def test_list_categories_empty(client):
    r = client.get("/api/v1/categories/")
    assert r.status_code == 200
    assert r.json() == []


def test_create_category_as_admin(client):
    token = register_and_login(client, "admin@test.com", role="admin", name="Admin")
    r = client.post("/api/v1/categories/", json={"name": "Cabelo", "icon": "scissors"}, headers=auth_header(token))
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Cabelo"
    assert data["icon"] == "scissors"
    assert data["is_active"] is True


def test_create_category_as_client_forbidden(client):
    token = register_and_login(client, "client@test.com", role="client")
    r = client.post("/api/v1/categories/", json={"name": "Unhas"}, headers=auth_header(token))
    assert r.status_code == 403


def test_create_category_without_auth(client):
    r = client.post("/api/v1/categories/", json={"name": "Unhas"})
    assert r.status_code == 401


def test_create_duplicate_category(client):
    token = register_and_login(client, "admin2@test.com", role="admin", name="Admin2")
    client.post("/api/v1/categories/", json={"name": "Maquiagem"}, headers=auth_header(token))
    r = client.post("/api/v1/categories/", json={"name": "Maquiagem"}, headers=auth_header(token))
    assert r.status_code == 409


def test_list_categories_with_data(client):
    token = register_and_login(client, "admin3@test.com", role="admin", name="Admin3")
    client.post("/api/v1/categories/", json={"name": "Sobrancelha"}, headers=auth_header(token))
    client.post("/api/v1/categories/", json={"name": "Barba"}, headers=auth_header(token))

    r = client.get("/api/v1/categories/")
    assert r.status_code == 200
    names = [c["name"] for c in r.json()]
    assert "Sobrancelha" in names
    assert "Barba" in names


def test_update_category(client):
    token = register_and_login(client, "admin4@test.com", role="admin", name="Admin4")
    created = client.post("/api/v1/categories/", json={"name": "Pele"}, headers=auth_header(token))
    cat_id = created.json()["id"]

    r = client.patch(f"/api/v1/categories/{cat_id}", json={"name": "Skincare", "is_active": True}, headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["name"] == "Skincare"
