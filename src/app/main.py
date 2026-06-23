from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.cache.redis import redis_client
from app.infrastructure.config.logger import logger, setup_logging
from app.infrastructure.config.settings import settings
from app.infrastructure.db.session import engine
from app.presentation.api.v1.endpoints.health import router as health_router
from app.presentation.api.v1.router import v1_router
from app.presentation.exception_handlers import register_exception_handlers
from app.presentation.middlewares.accept import AcceptMiddleware
from app.presentation.middlewares.content_type import ContentTypeMiddleware
from app.presentation.middlewares.rate_limit import RateLimitMiddleware
from app.presentation.middlewares.request_id import RequestIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona el ciclo de vida de la aplicación FastAPI (inicio y apagado)."""
    setup_logging(settings.APP_ENV)
    logger.info("app_starting", env=settings.APP_ENV, version=settings.APP_VERSION)
    yield
    await engine.dispose()
    await redis_client.close()
    logger.info("app_shutdown")


app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION, lifespan=lifespan)

# --- Registro de Manejadores de Excepciones ---
register_exception_handlers(app)

# --- Registro de Middlewares (el último añadido se ejecuta primero) ---
app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
app.add_middleware(AcceptMiddleware)
app.add_middleware(ContentTypeMiddleware, strict_jsonapi=settings.STRICT_JSONAPI)
app.add_middleware(RequestIdMiddleware)

# --- Registro de Enrutadores ---
app.include_router(health_router)   
app.include_router(v1_router)