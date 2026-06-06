"""Fábricas de dependencias base compartidas por todos los módulos del container."""

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.services.authorization_service import AuthorizationService
from app.infrastructure.cache.redis import get_redis, redis_client
from app.infrastructure.db.session import engine
from app.infrastructure.events.bus import LoggingEventBus
from app.infrastructure.security.authorization import RbacAuthorizationService
from app.infrastructure.security.hashing import BcryptPasswordHasher
from app.infrastructure.security.jwt import PyJwtTokenService
from app.infrastructure.uow import SqlAlchemyUnitOfWork


def get_uow() -> UnitOfWorkPort:
    """Fábrica de dependencias para el Unit of Work de SQLAlchemy, inyectando el bus de eventos."""
    return SqlAlchemyUnitOfWork(event_bus=LoggingEventBus())



def get_password_hasher() -> PasswordHasherPort:
    """Fábrica de dependencias para el servicio de hashing con Bcrypt."""
    return BcryptPasswordHasher()


async def get_token_service(redis: Redis = Depends(get_redis)) -> TokenServicePort:
    """Fábrica de dependencias para el servicio de tokens JWT con Redis."""
    return PyJwtTokenService(redis)


async def get_authorization_service(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> AuthorizationService:
    """Fábrica de dependencias para el servicio de autorización RBAC."""
    return RbacAuthorizationService(uow)


def get_db_engine() -> AsyncEngine:
    """Devuelve la instancia global de AsyncEngine."""
    return engine


def get_redis_client() -> Redis:
    """Devuelve el cliente global de Redis."""
    return redis_client  # type: ignore[no-any-return]
