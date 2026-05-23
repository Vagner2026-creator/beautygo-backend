from app.tests.conftest import register_and_login, auth_header


def _setup(client):
    """Cria profissional+perfil e cliente+perfil. Retorna (cli_token, pro_id)."""
    pro_token = register_and_login(client, "pro@rev.com", role="professional", name="Pro")
    pro = client.post("/api/v1/professionals/", json={"business_name": "Studio"}, headers=auth_header(pro_token))
    pro_id = pro.json()["id"]

    cli_token = register_and_login(client, "cli@rev.com", role="client", name="Cliente")
    client.post("/api/v1/clients/", json={}, headers=auth_header(cli_token))

    return cli_token, pro_id


def test_create_review(client):
    cli_token, pro_id = _setup(client)

    r = client.post("/api/v1/reviews/", json={
        "professional_id": pro_id,
        "rating": 5,
        "comment": "Excelente serviço!",
    }, headers=auth_header(cli_token))

    assert r.status_code == 201
    data = r.json()
    assert data["rating"] == 5
    assert data["comment"] == "Excelente serviço!"
    assert data["professional_id"] == pro_id


def test_create_review_updates_rating(client):
    cli_token, pro_id = _setup(client)

    client.post("/api/v1/reviews/", json={
        "professional_id": pro_id, "rating": 4,
    }, headers=auth_header(cli_token))

    r = client.get(f"/api/v1/professionals/{pro_id}")
    assert r.status_code == 200
    data = r.json()
    assert float(data["rating"]) == 4.0
    assert data["rating_count"] == 1


def test_create_review_invalid_rating(client):
    cli_token, pro_id = _setup(client)

    r = client.post("/api/v1/reviews/", json={
        "professional_id": pro_id, "rating": 6,
    }, headers=auth_header(cli_token))
    assert r.status_code == 422


def test_create_duplicate_review(client):
    cli_token, pro_id = _setup(client)

    client.post("/api/v1/reviews/", json={"professional_id": pro_id, "rating": 3},
                headers=auth_header(cli_token))
    r = client.post("/api/v1/reviews/", json={"professional_id": pro_id, "rating": 5},
                    headers=auth_header(cli_token))
    assert r.status_code == 409


def test_create_review_not_client(client):
    pro_token = register_and_login(client, "pro2@rev.com", role="professional", name="Pro2")
    pro = client.post("/api/v1/professionals/", json={"business_name": "Outro Studio"},
                      headers=auth_header(pro_token))
    pro_id = pro.json()["id"]

    r = client.post("/api/v1/reviews/", json={"professional_id": pro_id, "rating": 5},
                    headers=auth_header(pro_token))
    assert r.status_code == 403


def test_list_reviews(client):
    cli_token, pro_id = _setup(client)
    client.post("/api/v1/reviews/", json={"professional_id": pro_id, "rating": 4, "comment": "Bom"},
                headers=auth_header(cli_token))

    r = client.get(f"/api/v1/reviews/professionals/{pro_id}/reviews")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["rating"] == 4


def test_list_reviews_empty(client):
    pro_token = register_and_login(client, "pro3@rev.com", role="professional", name="Pro3")
    pro = client.post("/api/v1/professionals/", json={"business_name": "Empty Studio"},
                      headers=auth_header(pro_token))
    pro_id = pro.json()["id"]

    r = client.get(f"/api/v1/reviews/professionals/{pro_id}/reviews")
    assert r.status_code == 200
    assert r.json()["total"] == 0
