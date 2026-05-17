# BeautyGO Backend API

Marketplace de serviços de beleza — conecta clientes a profissionais (salões, manicures, cabeleireiros, etc.).

## Stack Tecnológico

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework | FastAPI 0.111 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Banco de Dados | PostgreSQL 16 |
| Cache / Rate Limit | Redis 7 |
| Autenticação | JWT (python-jose) + bcrypt |
| Validação | Pydantic v2 |
| Monitoramento | Prometheus + Grafana |
| Error Tracking | Sentry (opcional) |
| Orquestração | Docker Compose |

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.12+ (para desenvolvimento local sem Docker)

---

## Como Rodar com Docker

```bash
# 1. Copie e edite as variáveis de ambiente
cp .env.example .env

# 2. Suba todos os serviços (API, PostgreSQL, Redis, Prometheus, Grafana)
docker compose up --build

# 3. A API estará disponível em:
#    http://localhost:8000
#    Docs (apenas DEBUG=true): http://localhost:8000/docs
#    Redoc (apenas DEBUG=true): http://localhost:8000/redoc
```

---

## Como Rodar Localmente

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais locais

# 4. Execute as migrações
alembic upgrade head

# 5. Suba a API com reload automático
uvicorn app.main:app --reload --port 8000
```

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | URL de conexão PostgreSQL | obrigatório |
| `REDIS_URL` | URL de conexão Redis | `redis://localhost:6379/0` |
| `SECRET_KEY` | Chave secreta JWT (mínimo 32 caracteres) | obrigatório |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (minutos) | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` |
| `DEBUG` | Habilita /docs e /redoc | `false` |
| `ENVIRONMENT` | Ambiente (development/production) | `development` |
| `APP_NAME` | Nome da aplicação | `BeautyGO API` |
| `APP_VERSION` | Versão da aplicação | `1.0.0` |
| `CORS_ORIGINS` | Origens permitidas (vírgula separado) | `http://localhost:3000` |
| `SENTRY_DSN` | DSN do Sentry (opcional) | vazio |
| `RATE_LIMIT_PER_MINUTE` | Limite de requisições por minuto por IP | `60` |

---

## Migrações com Alembic

```bash
# Criar nova migration
alembic revision --autogenerate -m "descricao da mudanca"

# Aplicar todas as migrations pendentes
alembic upgrade head

# Reverter a última migration
alembic downgrade -1

# Ver histórico de migrations
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

### Categorias (`/api/v1/categories`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/` | Listar categorias | Não |
| POST | `/` | Criar categoria | Admin |
| PATCH | `/{id}` | Atualizar categoria | Admin |
| DELETE | `/{id}` | Deletar categoria | Admin |

### Serviços (`/api/v1/services`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/professionals/{id}/services` | Listar serviços de um profissional | Não |
| POST | `/` | Criar serviço | Profissional |
| PATCH | `/{service_id}` | Atualizar serviço | Profissional |
| DELETE | `/{service_id}` | Deletar serviço | Profissional |

### Agendamentos (`/api/v1/appointments`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| POST | `/` | Criar agendamento | Cliente |
| GET | `/client` | Listar agendamentos do cliente | Cliente |
| GET | `/professional` | Listar agendamentos do profissional | Profissional |
| GET | `/{appointment_id}` | Detalhes do agendamento | Cliente ou Profissional |
| PATCH | `/{appointment_id}/confirm` | Confirmar agendamento | Profissional |
| PATCH | `/{appointment_id}/cancel` | Cancelar agendamento | Cliente ou Profissional |
| PATCH | `/{appointment_id}/reschedule` | Reagendar | Cliente |

### Disponibilidade (`/api/v1/availability`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/professional/{id}` | Ver disponibilidade do profissional | Não |
| GET | `/professional/{id}/slots?date=&service_id=` | Slots disponíveis para agendamento | Não |
| POST | `/` | Criar disponibilidade semanal | Profissional |
| PATCH | `/{availability_id}` | Atualizar disponibilidade | Profissional |
| DELETE | `/{availability_id}` | Deletar disponibilidade | Profissional |
| POST | `/block-date` | Bloquear data específica | Profissional |
| DELETE | `/block-date/{blocked_id}` | Desbloquear data | Profissional |

### Notificações (`/api/v1/notifications`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/` | Listar notificações | Sim |
| PATCH | `/{notification_id}/read` | Marcar notificação como lida | Sim |
| PATCH | `/read-all` | Marcar todas como lidas | Sim |

### Galeria (`/api/v1/media`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| POST | `/` | Upload de imagem | Profissional |
| GET | `/professionals/{id}/media` | Listar galeria do profissional | Não |
| DELETE | `/{media_id}` | Deletar imagem | Profissional |

### Avaliações (`/api/v1/reviews`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/professionals/{id}/reviews` | Listar avaliações do profissional | Não |
| POST | `/` | Criar avaliação | Cliente |

### Favoritos (`/api/v1/favorites`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/` | Listar favoritos | Cliente |
| POST | `/` | Adicionar favorito | Cliente |
| DELETE | `/{professional_id}` | Remover favorito | Cliente |

### Busca (`/api/v1/search`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/` | Buscar profissionais (filtros avançados) | Não |

### Admin (`/api/v1/admin`)

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/stats` | Estatísticas gerais | Admin |
| GET | `/users` | Listar todos os usuários | Admin |
| GET | `/professionals` | Listar profissionais | Admin |
| PATCH | `/professionals/{id}/verify` | Verificar profissional | Admin |
| PATCH | `/users/{id}/block` | Bloquear usuário | Admin |
| GET | `/reports` | Relatório de agendamentos | Admin |

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
│   │   └── routes/              # Endpoints FastAPI
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── clients.py
│   │       ├── professionals.py
│   │       ├── locations.py
│   │       ├── admin.py
│   │       ├── categories.py
│   │       ├── services.py
│   │       ├── media.py
│   │       ├── reviews.py
│   │       ├── favorites.py
│   │       ├── search.py
│   │       ├── appointments.py  # Etapa 3
│   │       ├── availability.py  # Etapa 3
│   │       └── notifications.py # Etapa 3
│   ├── core/                    # Configurações centrais
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── database.py          # Engine SQLAlchemy + Base
│   │   ├── dependencies.py      # Injeção de dependências FastAPI
│   │   ├── limiter.py           # Rate limiting (slowapi)
│   │   ├── middleware.py        # Security headers + Audit log
│   │   ├── security.py          # JWT + bcrypt
│   │   └── utils.py             # CPF, slug, telefone
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── professional.py      # + campo is_verified (Etapa 3)
│   │   ├── city.py / state.py
│   │   ├── audit_log.py
│   │   ├── category.py
│   │   ├── professional_service.py
│   │   ├── professional_media.py
│   │   ├── review.py
│   │   ├── favorite.py
│   │   ├── search_log.py
│   │   ├── availability.py      # Etapa 3
│   │   ├── blocked_date.py      # Etapa 3
│   │   ├── appointment.py       # Etapa 3
│   │   ├── notification.py      # Etapa 3
│   │   └── admin_log.py         # Etapa 3
│   ├── repositories/            # Camada de acesso ao banco
│   ├── schemas/                 # Schemas Pydantic (request/response)
│   ├── services/                # Regras de negócio
│   ├── middlewares/             # Middlewares extras
│   ├── tests/                   # Testes automatizados
│   └── main.py                  # Ponto de entrada FastAPI
├── alembic/                     # Migrações de banco
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── prometheus.yml
├── requirements.txt
├── README.md
├── DEPLOY.md
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

---

## Checklist de Funcionalidades

### Etapa 1 — Base
- [x] Autenticação (registro, login, refresh, troca de senha)
- [x] CRUD de usuários
- [x] Perfis de cliente e profissional
- [x] Localização (estados e cidades)
- [x] Painel admin básico (stats)
- [x] Rate limiting, CORS, security headers
- [x] Audit log de requisições
- [x] Sentry para error tracking
- [x] Docker Compose completo

### Etapa 2 — Marketplace
- [x] Categorias de serviços
- [x] Serviços do profissional (CRUD)
- [x] Galeria de fotos (upload/delete)
- [x] Avaliações e rating médio
- [x] Favoritos
- [x] Busca avançada com filtros e geolocalização

### Etapa 3 — Agendamentos
- [x] Disponibilidade semanal do profissional
- [x] Bloqueio de datas específicas
- [x] Slots disponíveis por data e serviço
- [x] Agendamentos (criar, confirmar, cancelar, reagendar)
- [x] Notificações internas (novo agendamento, confirmação, cancelamento)
- [x] Painel admin expandido (listar usuários, verificar profissional, bloquear usuário, relatórios)
- [x] Campo is_verified no profissional
- [x] Log de ações administrativas (admin_log)
