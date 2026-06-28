"""Entidad de dominio para Intervención Técnica."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.identifier import InterventionId, UserId, WorkOrderId


@dataclass(frozen=True)
class TechnicalIntervention:
    """Intervención técnica realizada dentro de una orden de trabajo."""

    id: InterventionId
    work_order_id: WorkOrderId
    technician_id: UserId
    tareas_realizadas: str
    fecha_inicio: datetime
    fecha_fin: datetime | None
    horas_hombre: float

    def __post_init__(self) -> None:
        """Valida las invariantes de la entidad.

        Raises:
            ValueError: Si horas_hombre es negativo o fecha_fin es anterior a fecha_inicio.
        """
        if self.horas_hombre < 0:
            raise ValueError("horas_hombre no puede ser negativo")
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")

    @classmethod
    def create(
        cls,
        work_order_id: WorkOrderId,
        technician_id: UserId,
        tareas_realizadas: str,
        fecha_inicio: datetime,
        horas_hombre: float,
    ) -> "TechnicalIntervention":
        """Crea una nueva intervención técnica.

        Args:
            work_order_id: Identificador de la orden de trabajo asociada.
            technician_id: Identificador del técnico asignado.
            tareas_realizadas: Descripción detallada de las tareas realizadas.
            fecha_inicio: Fecha y hora de inicio.
            horas_hombre: Horas hombre dedicadas a la intervención.

        Returns:
            Una nueva instancia de TechnicalIntervention.
        """
        return cls(
            id=InterventionId.generar(),
            work_order_id=work_order_id,
            technician_id=technician_id,
            tareas_realizadas=tareas_realizadas,
            fecha_inicio=fecha_inicio,
            fecha_fin=None,
            horas_hombre=horas_hombre,
        )
