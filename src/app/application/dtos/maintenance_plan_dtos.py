"""DTOs para el módulo MaintenancePlan (Plan de Mantenimiento)."""

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(frozen=True)
class MaintenancePlanResponse:
    """DTO de salida con los datos de un plan de mantenimiento."""

    id: str
    empresa_id: str
    activo_id: str
    nombre: str
    tipo: str
    intervalo_dias: int
    proxima_ejecucion: date
    tecnico_responsable_id: str | None = None
    descripcion_tareas: str | None = None
    activo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    es_urgente: bool = False


@dataclass
class CreateMaintenancePlanRequest:
    """DTO de entrada para crear un plan de mantenimiento."""

    activo_id: str
    nombre: str
    tipo: str
    intervalo_dias: int
    proxima_ejecucion: date
    tecnico_responsable_id: str | None = None
    descripcion_tareas: str | None = None


@dataclass
class UpdateMaintenancePlanRequest:
    """DTO de entrada para actualizar un plan de mantenimiento.

    Todos los campos son opcionales; solo se actualizan los provistos.
    ``_fields_set`` se auto-puebla en ``__post_init__`` con los campos
    cuyo valor no es ``None`` (excepto el propio ``_fields_set``).
    """

    nombre: str | None = None
    tipo: str | None = None
    intervalo_dias: int | None = None
    proxima_ejecucion: date | None = None
    tecnico_responsable_id: str | None = None
    descripcion_tareas: str | None = None
    activo: bool | None = None
    _fields_set: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Auto-puebla ``_fields_set`` con los campos no-None provistos."""
        if not self._fields_set:
            object.__setattr__(
                self,
                "_fields_set",
                frozenset(
                    k for k, v in self.__dict__.items()
                    if v is not None and k != "_fields_set"
                ),
            )
