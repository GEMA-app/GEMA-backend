import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

# Registry automático para reconstrucción de eventos en outbox (Sprint V)
_EVENT_REGISTRY: dict[str, type["DomainEvent"]] = {}


def auto_register(cls: type["DomainEvent"]) -> type["DomainEvent"]:
    """Decorador que registra un DomainEvent en el _EVENT_REGISTRY para su reconstrucción."""
    _EVENT_REGISTRY[cls.__name__] = cls
    return cls


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Clase base para todos los eventos de dominio."""

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=lambda: datetime.now(UTC))


@runtime_checkable
class EventProducer(Protocol):
    """Protocol para entidades de dominio que producen eventos (reemplaza hasattr)."""

    def pull_events(self) -> list[DomainEvent]:
        """Extrae y limpia la lista de eventos acumulados."""
        ...


@auto_register
@dataclass(frozen=True, kw_only=True)
class UserRegistered(DomainEvent):
    """Evento emitido cuando un nuevo usuario se registra en el sistema."""

    user_id: str
    email: str
    nombre: str = ""
    empresa_id: str = ""
    company_name: str = ""


@auto_register
@dataclass(frozen=True, kw_only=True)
class UserLoggedIn(DomainEvent):
    """Evento emitido cuando un usuario inicia sesión exitosamente."""

    user_id: str
    email: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class CompanyCreated(DomainEvent):
    """Evento emitido cuando se crea una nueva empresa (tenant) en la plataforma."""

    company_id: str
    nombre: str
    slug: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class RoleAssigned(DomainEvent):
    """Evento emitido cuando se asigna un rol a un usuario."""

    user_id: str
    role_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class RoleRevoked(DomainEvent):
    """Evento emitido cuando se revoca un rol a un usuario."""

    user_id: str
    role_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class PasswordChanged(DomainEvent):
    """Evento emitido cuando un usuario cambia su contraseña."""

    user_id: str
    email: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class PasswordResetInitiated(DomainEvent):
    """Evento de auditoría emitido cuando un usuario solicita un reset de contraseña.

    El email con el raw_token se envía directamente desde el use case para evitar
    que el token se serialice en una tabla outbox.
    """

    user_id: str
    email: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class PasswordResetCompleted(DomainEvent):
    """Evento emitido cuando un usuario completa el reset de contraseña."""

    user_id: str
    email: str
