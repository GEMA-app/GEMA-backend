"""Eventos de dominio del sistema GEMA."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

# Registry automático para reconstrucción de eventos en outbox (Sprint V)
_event_registry: dict[str, type["DomainEvent"]] = {}


def auto_register(cls: type["DomainEvent"]) -> type["DomainEvent"]:
    """Decorador que registra un DomainEvent en el _event_registry para su reconstrucción.

    Args:
        cls: La clase DomainEvent a registrar.

    Returns:
        La misma clase sin modificar (decorador de identidad).
    """
    _event_registry[cls.__name__] = cls
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
        """Extrae y limpia la lista de eventos acumulados.

        Returns:
            La lista de eventos de dominio acumulados, vaciando la lista interna.
        """
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
class UserDeactivated(DomainEvent):
    """Evento emitido cuando un usuario es desactivado (baja lógica)."""

    user_id: str
    email: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class UserActivated(DomainEvent):
    """Evento emitido cuando un usuario desactivado es reactivado."""

    user_id: str
    email: str


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


@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetCreated(DomainEvent):
    """Evento emitido cuando se crea un nuevo activo en el sistema."""

    asset_id: str
    empresa_id: str
    codigo_activo: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetMaintenanceStarted(DomainEvent):
    """Evento emitido cuando un activo pasa a estado de mantenimiento."""

    asset_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetDecommissioned(DomainEvent):
    """Evento emitido cuando un activo es dado de baja."""

    asset_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetPutInService(DomainEvent):
    """Evento emitido cuando un activo vuelve a estado operativo."""

    asset_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetOutOfService(DomainEvent):
    """Evento emitido cuando un activo pasa a fuera de servicio."""

    asset_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetUpdated(DomainEvent):
    """Evento emitido cuando se actualizan los atributos base de un activo."""

    asset_id: str
    empresa_id: str
    codigo_activo: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetLocationChanged(DomainEvent):
    """Evento emitido cuando un activo cambia de ubicación."""

    asset_id: str
    previous_location_id: str | None
    new_location_id: str | None


@auto_register
@dataclass(frozen=True, kw_only=True)
class FailureReportCreated(DomainEvent):
    """Evento emitido cuando se crea un nuevo reporte de falla."""

    failure_report_id: str
    empresa_id: str
    title: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class LocationCreated(DomainEvent):
    """Evento emitido cuando se crea una nueva ubicación."""

    location_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class LocationMoved(DomainEvent):
    """Evento emitido cuando una ubicación cambia de padre."""

    location_id: str
    previous_parent_id: str | None
    new_parent_id: str | None


@auto_register
@dataclass(frozen=True, kw_only=True)
class CompanySuspended(DomainEvent):
    """Evento emitido cuando una empresa es suspendida."""

    company_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class CompanyActivated(DomainEvent):
    """Evento emitido cuando una empresa suspendida es reactivada."""

    company_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class CompanyCancelled(DomainEvent):
    """Evento emitido cuando una empresa es cancelada definitivamente."""

    company_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class CompanyProfileUpdated(DomainEvent):
    """Evento emitido cuando se actualiza el perfil de una empresa."""

    company_id: str
