# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BeautyGO is a marketplace backend connecting clients to beauty professionals (salons, manicurists, hairdressers, etc.). Built with Python/FastAPI, PostgreSQL, and Redis.

## Common Commands

All commands run from `backend/`:

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
cp .env.example .env          # then fill in required values

# Run dev server
uvicorn app.main:app --reload --port 8000

# Database migrations
alembic upgrade head           # apply all migrations
alembic revision --autogenerate -m "description"  # generate new migration

# Tests
pytest app/tests/ -v
pytest app/tests/test_auth.py -v          # single test file
pytest app/tests/test_auth.py::test_name  # single test

# Docker (full stack)
docker compose up --build
```

Required `.env` variables: `DATABASE_URL`, `SECRET_KEY` (min 32 chars).

## Architecture

The project follows a layered architecture with strict separation: **Route → Service → Repository → Model**.

```
app/
├── main.py           # FastAPI app creation, middleware registration, router inclusion
├── api/routes/       # HTTP layer only — no business logic
├── services/         # Business logic — instantiated per-request, receive db session
├── repositories/     # DB queries via SQLAlchemy — one class per model
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic models for request/response validation
├── core/
│   ├── config.py     # pydantic-settings Settings class, loaded from .env
│   ├── database.py   # engine, SessionLocal, Base, get_db() dependency
│   ├── security.py   # JWT creation/decoding, bcrypt password hashing
│   ├── dependencies.py  # FastAPI dependencies: get_current_user, get_current_active_admin, get_current_professional
│   ├── middleware.py  # SecurityHeadersMiddleware, AuditMiddleware
│   └── limiter.py    # slowapi instance (rate limit by IP)
```

### Key Patterns

**Authentication flow:** Routes use `Depends(get_current_user)` from `core/dependencies.py`. This validates the Bearer JWT (type=`"access"`), looks up the user via `UserRepository`, and returns the `User` model. Role checks use `get_current_active_admin` or `get_current_professional`.

**Service instantiation:** Services are instantiated inside route handlers with the `db` session (`AuthService(db)`), not as singletons.

**Repository pattern:** All DB queries go through repository classes. Repositories receive a `Session` in `__init__` and expose typed methods. Never query the DB directly from routes or services.

**JWT tokens:** Two token types — `access` (30 min, payload includes `role`) and `refresh` (7 days). `verify_token_type(token, type)` validates both signature and type claim.

**User roles:** `UserRole` enum in `app/models/user.py` — `ADMIN`, `CLIENT`, `PROFESSIONAL`. Role is stored in the DB and embedded in the access token payload.

### Testing

Tests use SQLite in-memory (`sqlite:///./test.db`) via `conftest.py`, which overrides the `get_db` dependency. Each test function gets a fresh DB (tables created and dropped per function). Use `client` fixture for HTTP tests and `db` fixture for repository/service tests.

### Docker Services

| Service | Port | Notes |
|---|---|---|
| api | 8000 | FastAPI with hot reload |
| db | 5432 | PostgreSQL 16 |
| redis | 6379 | Redis 7 |
| prometheus | 9090 | Scrapes api:8000 every 15s |
| grafana | 3001 | admin/admin123 |

`alembic.ini` hardcodes a local PostgreSQL URL — override via `DATABASE_URL` env var when running outside Docker.
