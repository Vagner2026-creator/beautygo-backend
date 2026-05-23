from app.tests.conftest import register_and_login, auth_header


def _setup(client):
    """Cria profissional+perfil e cliente+perfil. Retorna (cli_token, pro_id)."""
    pro_token = register_and_login(client, "pro@fav.com", role="professional", name="Pro")
    pro = client.post("/api/v1/professionals/", json={"business_name": "Studio"}, headers=auth_header(pro_token))
    pro_id = pro.json()["id"]

    cli_token = register_and_login(client, "cli@fav.com", role="client", name="Cliente")
    client.post("/api/v1/clients/", json={}, headers=auth_header(cli_token))

    return cli_token, pro_id


def test_add_favorite(client):
    cli_token, pro_id = _setup(client)

    r = client.post(f"/api/v1/favorites/{pro_id}", headers=auth_header(cli_token))
    assert r.status_code == 201
    assert r.json()["professional_id"] == pro_id


def test_add_favorite_requires_auth(client):
    _, pro_id = _setup(client)
    r = client.post(f"/api/v1/favorites/{pro_id}")
    assert r.status_code == 401


def test_add_duplicate_favorite(client):
    cli_token, pro_id = _setup(client)

    client.post(f"/api/v1/favorites/{pro_id}", headers=auth_header(cli_token))
    r = client.post(f"/api/v1/favorites/{pro_id}", headers=auth_header(cli_token))
    assert r.status_code == 409


def test_list_favorites(client):
    cli_token, pro_id = _setup(client)
    client.post(f"/api/v1/favorites/{pro_id}", headers=auth_header(cli_token))

    # GET /favorites/ retorna List[FavoriteResponse] (lista simples)
    r = client.get("/api/v1/favorites/", headers=auth_header(cli_token))
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["professional_id"] == pro_id


def test_list_favorites_empty(client):
    cli_token, _ = _setup(client)

    r = client.get("/api/v1/favorites/", headers=auth_header(cli_token))
    assert r.status_code == 200
    assert r.json() == []


def test_remove_favorite(client):
    cli_token, pro_id = _setup(client)
    client.post(f"/api/v1/favorites/{pro_id}", headers=auth_header(cli_token))

    r = client.delete(f"/api/v1/favorites/{pro_id}", headers=auth_header(cli_token))
    assert r.status_code == 204

    r = client.get("/api/v1/favorites/", headers=auth_header(cli_token))
    assert r.json() == []


def test_remove_nonexistent_favorite(client):
    cli_token, _ = _setup(client)
    r = client.delete("/api/v1/favorites/99999", headers=auth_header(cli_token))
    assert r.status_code == 404
