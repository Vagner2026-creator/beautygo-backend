# BeautyGO Backend API

Marketplace de serviços de beleza — conecta clientes a profissionais (salões, manicures, cabeleireiros, etc.).

## Tecnologias

- **Python 3.12** + **FastAPI 0.111**
- **PostgreSQL 16** via SQLAlchemy 2.0 + Alembic
- **Redis 7** para cache e rate limiting
- **JWT** (python-jose) para autenticação
- **Docker Compose** para orquestração local
- **Prometheus + Grafana** para observabilidade

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.12+ (para desenvolvimento local sem Docker)

---

## Subindo com Docker Compose

```bash
# Copie e edite as variáveis de ambiente
cp .env.example .env

# Suba todos os serviços
docker compose up --build

# A API estará disponível em:
# http://localhost:8000
# Docs (apenas DEBUG=true): http://localhost:8000/docs
```

---

## Desenvolvimento local (sem Docker)

```bash
# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais locais

# Execute as migrações
alembic upgrade head

# Suba a API com reload
uvicorn app.main:app --reload --port 8000
```

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | URL de conexão PostgreSQL | obrigatório |
| `REDIS_URL` | URL de conexão Redis | `redis://localhost:6379/0` |
| `SECRET_KEY` | Chave secreta JWT (min 32 chars) | obrigatório |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token | `7` |
| `DEBUG` | Habilita /docs e /redoc | `false` |
| `ENVIRONMENT` | Ambiente (development/production) | `development` |
| `CORS_ORIGINS` | Origens permitidas (vírgula separado) | `http://localhost:3000` |
| `SENTRY_DSN` | DSN do Sentry (opcional) | vazio |
| `RATE_LIMIT_PER_MINUTE` | Limite de requisições por minuto | `60` |

---

## Migrações com Alembic

```bash
# Criar nova migration
alembic revision --autogenerate -m "descricao da mudanca"

# Aplicar todas as migrations pendentes
alembic upgrade head

# Reverter a última migration
alembic downgrade -1

# Ver histórico
alembic history
```

---

## Endpoints Principais

### Autenticação (`/api/v1/auth`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| POST | `/register` | Cadastrar novo usuário | Não |
| POST | `/login` | Login e geração de tokens | Não |
| POST | `/refresh` | Renovar access token | Não |
| POST | `/change-password` | Alterar senha | Sim |
| GET | `/me` | Dados do usuário autenticado | Sim |

### Usuários (`/api/v1/users`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/` | Listar todos os usuários | Admin |
| GET | `/{user_id}` | Buscar usuário por ID | Admin |
| PATCH | `/me` | Atualizar dados próprios | Sim |
| DELETE | `/{user_id}` | Desativar usuário | Admin |

### Clientes (`/api/v1/clients`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| POST | `/` | Criar perfil de cliente | Sim |
| GET | `/me` | Ver perfil de cliente | Sim |
| PATCH | `/me` | Atualizar perfil de cliente | Sim |

### Profissionais (`/api/v1/professionals`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/` | Listar profissionais (filtros: city_id, specialty, available_only) | Não |
| POST | `/` | Criar perfil profissional | Sim |
| GET | `/me` | Ver meu perfil profissional | Profissional |
| PATCH | `/me` | Atualizar meu perfil profissional | Profissional |
| GET | `/{professional_id}` | Ver perfil de um profissional | Não |

### Localização (`/api/v1/locations`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/states` | Listar estados | Não |
| GET | `/states/{state_id}/cities` | Listar cidades do estado | Não |
| GET | `/cities/search?name=` | Buscar cidades por nome | Não |
| GET | `/cities/{city_id}` | Buscar cidade por ID | Não |

### Admin (`/api/v1/admin`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/stats` | Estatísticas gerais da plataforma | Admin |

### Health Check

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Status da API |

---

## Executando os Testes

```bash
# Instale dependências de teste (já incluídas no requirements.txt)
pip install -r requirements.txt

# Execute todos os testes
pytest app/tests/ -v

# Execute com cobertura
pytest app/tests/ -v --tb=short

# Executar arquivo específico
pytest app/tests/test_auth.py -v
pytest app/tests/test_security.py -v
pytest app/tests/test_users.py -v
```

Os testes usam SQLite em memória — não é necessário PostgreSQL rodando.

---

## Observabilidade

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin / admin123)

---

## Estrutura do Projeto

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # Endpoints FastAPI
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── clients.py
│   │       ├── professionals.py
│   │       ├── locations.py
│   │       └── admin.py
│   ├── core/                # Configurações centrais
│   │   ├── config.py        # Settings via pydantic-settings
│   │   ├── database.py      # Engine SQLAlchemy + Base
│   │   ├── dependencies.py  # Injeção de dependências FastAPI
│   │   ├── limiter.py       # Rate limiting (slowapi)
│   │   ├── middleware.py    # Security headers + Audit log
│   │   ├── security.py      # JWT + bcrypt
│   │   └── utils.py         # CPF, slug, telefone
│   ├── models/              # Modelos SQLAlchemy
│   ├── repositories/        # Camada de acesso ao banco
│   ├── schemas/             # Schemas Pydantic (request/response)
│   ├── services/            # Regras de negócio
│   ├── middlewares/         # Middlewares extras
│   ├── tests/               # Testes automatizados
│   └── main.py              # Ponto de entrada FastAPI
├── alembic/                 # Migrações de banco
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── prometheus.yml
├── requirements.txt
└── .env.example
```

---

## Roles de Usuário

| Role | Descrição |
|---|---|
| `client` | Cliente que busca e contrata serviços |
| `professional` | Profissional que oferece serviços |
| `admin` | Administrador com acesso total |

---

## Segurança

- Senhas hasheadas com bcrypt
- JWT com access token (30min) e refresh token (7 dias)
- Rate limiting por IP (slowapi)
- Security headers em todas as respostas
- CORS configurável por variável de ambiente
- Validação de CPF no cadastro de clientes
