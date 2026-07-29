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
    empresa_id: str


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Activos â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class AssetDeleted(DomainEvent):
    """Evento emitido cuando un activo es eliminado."""

    asset_id: str
    codigo_activo: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ubicaciones â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class LocationUpdated(DomainEvent):
    """Evento emitido cuando se actualiza una ubicación."""

    location_id: str
    nombre: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class LocationDeleted(DomainEvent):
    """Evento emitido cuando se elimina una ubicación."""

    location_id: str
    nombre: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Roles â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class RoleCreated(DomainEvent):
    """Evento emitido cuando se crea un nuevo rol."""

    role_id: str
    nombre: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class RoleUpdated(DomainEvent):
    """Evento emitido cuando se actualiza un rol."""

    role_id: str
    nombre: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class RoleDeleted(DomainEvent):
    """Evento emitido cuando se elimina un rol."""

    role_id: str
    nombre: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Mantenimiento â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class FailureReportUpdated(DomainEvent):
    """Evento emitido cuando se actualiza un reporte de falla."""

    failure_report_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class FailureReportDeleted(DomainEvent):
    """Evento emitido cuando se elimina un reporte de falla."""

    failure_report_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class WorkOrderCreated(DomainEvent):
    """Evento emitido cuando se crea una orden de trabajo."""

    work_order_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class WorkOrderUpdated(DomainEvent):
    """Evento emitido cuando se actualiza una orden de trabajo."""

    work_order_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class WorkOrderDeleted(DomainEvent):
    """Evento emitido cuando se elimina una orden de trabajo."""

    work_order_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class MaintenancePlanCreated(DomainEvent):
    """Evento emitido cuando se crea un plan de mantenimiento."""

    maintenance_plan_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class MaintenancePlanUpdated(DomainEvent):
    """Evento emitido cuando se actualiza un plan de mantenimiento."""

    maintenance_plan_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class MaintenancePlanDeleted(DomainEvent):
    """Evento emitido cuando se elimina un plan de mantenimiento."""

    maintenance_plan_id: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Inventario â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class InventoryPartCreated(DomainEvent):
    """Evento emitido cuando se crea un repuesto en inventario."""

    part_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class InventoryPartUpdated(DomainEvent):
    """Evento emitido cuando se actualiza un repuesto en inventario."""

    part_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class InventoryPartDeleted(DomainEvent):
    """Evento emitido cuando se elimina un repuesto en inventario."""

    part_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class InventoryEntryCreated(DomainEvent):
    """Evento emitido cuando se crea un movimiento de inventario (entrada/salida)."""

    entry_id: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Proveedores â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class SupplierCreated(DomainEvent):
    """Evento emitido cuando se crea un proveedor."""

    supplier_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class SupplierUpdated(DomainEvent):
    """Evento emitido cuando se actualiza un proveedor."""

    supplier_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class SupplierDeleted(DomainEvent):
    """Evento emitido cuando se elimina un proveedor."""

    supplier_id: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Preferencias â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class PreferenceUpdated(DomainEvent):
    """Evento emitido cuando se actualizan las preferencias de un usuario."""

    user_id: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Intervenciones â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class InterventionCreated(DomainEvent):
    """Evento emitido cuando se crea una intervención técnica."""

    intervention_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class InterventionUpdated(DomainEvent):
    """Evento emitido cuando se actualiza una intervención técnica."""

    intervention_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class InterventionDeleted(DomainEvent):
    """Evento emitido cuando se elimina una intervención técnica."""

    intervention_id: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PlanExecution â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class PlanExecutionCreated(DomainEvent):
    """Evento emitido cuando se crea una ejecución de plan."""

    plan_execution_id: str
    empresa_id: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# UsedPart â€” faltantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@auto_register
@dataclass(frozen=True, kw_only=True)
class UsedPartCreated(DomainEvent):
    """Evento emitido cuando se registra un repuesto usado."""

    used_part_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class UsedPartUpdated(DomainEvent):
    """Evento emitido cuando se actualiza un repuesto usado."""

    used_part_id: str
    empresa_id: str


@auto_register
@dataclass(frozen=True, kw_only=True)
class UsedPartDeleted(DomainEvent):
    """Evento emitido cuando se elimina un repuesto usado."""

    used_part_id: str
    empresa_id: str
