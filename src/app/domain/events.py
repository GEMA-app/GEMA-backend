import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Clase base para todos los eventos de dominio."""
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class UserRegistered(DomainEvent):
    """Evento emitido cuando un nuevo usuario se registra en el sistema."""
    user_id: str
    email: str


@dataclass(frozen=True, kw_only=True)
class UserLoggedIn(DomainEvent):
    """Evento emitido cuando un usuario inicia sesión exitosamente."""
    user_id: str
    email: str


@dataclass(frozen=True, kw_only=True)
class CompanyCreated(DomainEvent):
    """Evento emitido cuando se crea una nueva empresa (tenant) en la plataforma."""
    company_id: str
    nombre: str
    slug: str


@dataclass(frozen=True, kw_only=True)
class RoleAssigned(DomainEvent):
    """Evento emitido cuando se asigna un rol a un usuario."""
    user_id: str
    role_id: str
    empresa_id: str


@dataclass(frozen=True, kw_only=True)
class RoleRevoked(DomainEvent):
    """Evento emitido cuando se revoca un rol a un usuario."""
    user_id: str
    role_id: str
    empresa_id: str

