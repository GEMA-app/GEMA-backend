"""Capa de Infrastructure: implementaciones concretas de los puertos definidos en Application."""

from app.infrastructure.cache.redis import RedisClient, get_redis, redis_client
from app.infrastructure.config.logger import setup_logging
from app.infrastructure.config.settings import Settings, settings
from app.infrastructure.events.bus import InProcessEventBus
from app.infrastructure.notifications.email_sender import (
    SmtpNotificationSender,
)
from app.infrastructure.security.authorization import RbacAuthorizationService
from app.infrastructure.security.hashing import BcryptPasswordHasher
from app.infrastructure.security.jwt import PyJwtTokenService
from app.infrastructure.uow import SqlAlchemyUnitOfWork

__all__ = [
    "Settings",
    "settings",
    "setup_logging",
    "RedisClient",
    "redis_client",
    "get_redis",
    "BcryptPasswordHasher",
    "PyJwtTokenService",
    "RbacAuthorizationService",
    "InProcessEventBus",
    "SmtpNotificationSender",
    "SqlAlchemyUnitOfWork",
]
