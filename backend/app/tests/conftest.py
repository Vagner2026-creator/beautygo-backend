import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db

# Banco em memória com StaticPool: mesma conexão compartilhada por todos os fixtures
# evita erros de lock do SQLite entre testes sequenciais
SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Limpa o storage do slowapi antes de cada teste para evitar erro 429."""
    from app.core.limiter import limiter
    if hasattr(limiter, "_storage") and hasattr(limiter._storage, "storage"):
        limiter._storage.storage.clear()
    yield


# ── Helpers compartilhados ────────────────────────────────────────────────────

def register_and_login(client_fixture, email, password="senha1234", name="User", role="client"):
    client_fixture.post("/api/v1/auth/register", json={
        "email": email, "password": password, "full_name": name, "role": role,
    })
    resp = client_fixture.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
