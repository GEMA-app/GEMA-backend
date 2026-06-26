"""DTOs para el módulo de intervenciones técnicas."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class InterventionResponse:
    """DTO de respuesta para una intervención técnica.

    Attributes:
        id: Identificador UUID de la intervención.
        work_order_id: Identificador UUID de la orden de trabajo asociada.
        technician_id: Identificador UUID del técnico asignado.
        tareas_realizadas: Descripción detallada de las tareas realizadas.
        fecha_inicio: Fecha y hora de inicio de la intervención.
        fecha_fin: Fecha y hora de finalización, o None si aún no ha terminado.
        horas_hombre: Total de horas hombre dedicadas a la intervención.
    """

    id: UUID
    work_order_id: UUID
    technician_id: UUID
    tareas_realizadas: str
    fecha_inicio: datetime
    fecha_fin: datetime | None
    horas_hombre: float


@dataclass(frozen=True)
class CreateInterventionRequest:
    """DTO para crear una nueva intervención técnica.

    Attributes:
        technician_id: Identificador UUID del técnico asignado.
        tareas_realizadas: Descripción detallada de las tareas realizadas.
        fecha_inicio: Fecha y hora de inicio de la intervención.
        horas_hombre: Total de horas hombre dedicadas a la intervención.
    """

    technician_id: UUID
    tareas_realizadas: str
    fecha_inicio: datetime
    horas_hombre: float


@dataclass(frozen=True)
class UpdateInterventionRequest:
    """DTO para actualizar una intervención técnica existente.

    Attributes:
        tareas_realizadas: Nueva descripción de tareas realizadas (opcional).
        horas_hombre: Nuevas horas hombre (opcional).
    """

    tareas_realizadas: str | None = None
    horas_hombre: float | None = None
