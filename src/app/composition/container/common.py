"""Fábricas de dependencias base compartidas por todos los módulos del container."""

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.notifications import NotificationPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.services.authorization_service import AuthorizationService
from app.domain.events import (
    PasswordChanged,
    PasswordResetCompleted,
    PasswordResetInitiated,
    UserRegistered,
)
from app.infrastructure.cache.redis import get_redis, redis_client
from app.infrastructure.db.session import engine
from app.infrastructure.events.bus import InProcessEventBus
from app.infrastructure.events.handlers.notifications import (
    handle_password_changed,
    handle_password_reset_completed,
    handle_password_reset_initiated,
    handle_user_registered,
)
from app.infrastructure.notifications.email_sender import SmtpNotificationSender
from app.infrastructure.security.authorization import RbacAuthorizationService
from app.infrastructure.security.hashing import BcryptPasswordHasher
from app.infrastructure.security.jwt import PyJwtTokenService
from app.infrastructure.uow import SqlAlchemyUnitOfWork

# Singletons con inicialización perezosa para evitar fallos en import time
# (si un template tiene error de sintaxis, no impide arrancar la app).
_notification_sender: SmtpNotificationSender | None = None
_event_bus: InProcessEventBus | None = None


def _ensure_bus() -> InProcessEventBus:
    """Devuelve la instancia singleton del bus de eventos, creándola si hace falta."""
    global _event_bus
    if _event_bus is None:
        _event_bus = InProcessEventBus()
        _register_handlers(_event_bus)
    return _event_bus


def _ensure_sender() -> SmtpNotificationSender:
    """Devuelve la instancia singleton del sender de notificaciones."""
    global _notification_sender
    if _notification_sender is None:
        _notification_sender = SmtpNotificationSender()
    return _notification_sender


def _register_handlers(bus: InProcessEventBus) -> None:
    """Registra los handlers de notificaciones en el bus de eventos.

    Args:
        bus: El bus de eventos donde se registrarán los handlers.
    """
    sender = _ensure_sender()
    # Las lambdas reciben DomainEvent (tipo del bus) y los handlers esperan subtipos
    # concretos. La coerción es segura porque el bus despacha por tipo concreto.
    bus.subscribe(
        UserRegistered, lambda e: handle_user_registered(e, sender)  # type: ignore[arg-type]
    )
    bus.subscribe(
        PasswordChanged, lambda e: handle_password_changed(e, sender)  # type: ignore[arg-type]
    )
    bus.subscribe(
        PasswordResetInitiated,
        lambda e: handle_password_reset_initiated(e, sender),  # type: ignore[arg-type]
    )
    bus.subscribe(
        PasswordResetCompleted,
        lambda e: handle_password_reset_completed(e, sender),  # type: ignore[arg-type]
    )


def get_uow() -> UnitOfWorkPort:
    """Fábrica de dependencias para el Unit of Work de SQLAlchemy.

    Returns:
        Una instancia de Unit of Work con el bus de eventos inyectado.
    """
    return SqlAlchemyUnitOfWork(event_bus=_ensure_bus())


def get_notification_sender() -> NotificationPort:
    """Fábrica de dependencias para el adaptador de notificaciones.

    Returns:
        El adaptador singleton de notificaciones (SMTP).
    """
    return _ensure_sender()


def get_password_hasher() -> PasswordHasherPort:
    """Fábrica de dependencias para el servicio de hashing con Bcrypt.

    Returns:
        Una instancia del servicio de hashing Bcrypt.
    """
    return BcryptPasswordHasher()


def create_token_service(redis_client: Redis) -> TokenServicePort:
    """Crea una instancia pura del servicio de tokens JWT.

    Args:
        redis_client: Cliente Redis para la blocklist de tokens.

    Returns:
        Una instancia del servicio de tokens JWT vinculada al cliente Redis.
    """
    return PyJwtTokenService(redis_client)


def create_authorization_service(uow: UnitOfWorkPort) -> AuthorizationService:
    """Crea una instancia pura del servicio de autorización RBAC.

    Args:
        uow: Unidad de trabajo para consultar roles y permisos.

    Returns:
        Una instancia del servicio de autorización RBAC.
    """
    return RbacAuthorizationService(uow)


async def get_token_service(redis: Redis = Depends(get_redis)) -> TokenServicePort:
    """Fábrica de dependencias para el servicio de tokens JWT con Redis.

    Args:
        redis: Cliente Redis inyectado por dependencia.

    Returns:
        El servicio de tokens JWT listo para ser inyectado.
    """
    return create_token_service(redis)


async def get_authorization_service(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> AuthorizationService:
    """Fábrica de dependencias para el servicio de autorización RBAC.

    Args:
        uow: Unidad de trabajo inyectada por dependencia.

    Returns:
        El servicio de autorización RBAC listo para ser inyectado.
    """
    return create_authorization_service(uow)


def get_db_engine() -> AsyncEngine:
    """Devuelve la instancia global de AsyncEngine.

    Returns:
        La instancia global de AsyncEngine de SQLAlchemy para PostgreSQL.
    """
    return engine


def get_redis_client() -> Redis:
    """Devuelve el cliente global de Redis.

    Returns:
        El cliente global de Redis.
    """
    from typing import cast
    return cast(Redis, redis_client)
