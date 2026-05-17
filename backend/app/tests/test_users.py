import pytest


def _create_and_login(client, email="u@test.com", password="senha1234", name="User"):
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": name})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def test_update_me(client):
    token = _create_and_login(client)
    response = client.patch(
        "/api/v1/users/me",
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


def test_update_me_unauthorized(client):
    response = client.patch("/api/v1/users/me", json={"full_name": "No Auth"})
    assert response.status_code == 401
