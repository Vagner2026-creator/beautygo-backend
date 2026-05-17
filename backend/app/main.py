import os
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.middleware import SecurityHeadersMiddleware, AuditMiddleware
from app.core.limiter import limiter
from app.api.routes import auth, users, clients, professionals, locations, admin
from app.api.routes import categories, services, media, reviews, favorites, search
from app.api.routes import appointments, availability, notifications

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="BeautyGO - Marketplace de Serviços de Beleza",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditMiddleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Usuários"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clientes"])
app.include_router(professionals.router, prefix="/api/v1/professionals", tags=["Profissionais"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["Localização"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categorias"])
app.include_router(services.router, prefix="/api/v1/services", tags=["Serviços"])
app.include_router(media.router, prefix="/api/v1/media", tags=["Galeria"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Avaliações"])
app.include_router(favorites.router, prefix="/api/v1/favorites", tags=["Favoritos"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Busca"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Agendamentos"])
app.include_router(availability.router, prefix="/api/v1/availability", tags=["Disponibilidade"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notificações"])

# Serve uploaded files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
