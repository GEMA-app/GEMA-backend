"""DTOs para el módulo de intervenciones técnicas."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import EstadoIntervencion


@dataclass(frozen=True)
class IntervencionResponse:
    """DTO de respuesta para una intervención técnica."""

    id: UUID
    orden_trabajo_id: UUID
    tecnico_id: UUID
    descripcion: str
    fecha_inicio: datetime
    fecha_fin: datetime | None
    horas_trabajadas: float
    costo: float
    estado: EstadoIntervencion
    observaciones: str | None


@dataclass(frozen=True)
class CrearIntervencionRequest:
    """DTO para crear una nueva intervención técnica."""

    orden_trabajo_id: UUID
    tecnico_id: UUID
    descripcion: str
    fecha_inicio: datetime
    horas_trabajadas: float
    costo: float
    observaciones: str | None = None


@dataclass(frozen=True)
class ActualizarIntervencionRequest:
    """DTO para actualizar una intervención técnica existente."""

    descripcion: str | None = None
    horas_trabajadas: float | None = None
    costo: float | None = None
    observaciones: str | None = None