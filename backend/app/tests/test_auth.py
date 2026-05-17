import pytest


def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@beautygo.com",
        "password": "senha1234",
        "full_name": "Test User",
        "role": "client"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@beautygo.com"
    assert data["role"] == "client"


def test_register_duplicate_email(client):
    payload = {"email": "dup@beautygo.com", "password": "senha1234", "full_name": "Dup User"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@beautygo.com", "password": "senha1234", "full_name": "Login User"
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "login@beautygo.com", "password": "senha1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "wrong@beautygo.com", "password": "senha1234", "full_name": "Wrong"
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@beautygo.com", "password": "senhaerrada"
    })
    assert response.status_code == 401


def test_me_endpoint(client):
    client.post("/api/v1/auth/register", json={
        "email": "me@beautygo.com", "password": "senha1234", "full_name": "Me User"
    })
    login = client.post("/api/v1/auth/login", json={
        "email": "me@beautygo.com", "password": "senha1234"
    })
    token = login.json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@beautygo.com"
