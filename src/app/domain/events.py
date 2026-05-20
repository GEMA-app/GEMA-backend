from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Clase base para todos los eventos de dominio."""
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


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
