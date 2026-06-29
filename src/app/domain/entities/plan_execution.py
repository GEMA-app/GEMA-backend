"""Entidad PlanExecution — ejecución de un plan de mantenimiento."""

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.domain.exceptions.plan_execution import (
    PlanExecutionObservationsEmptyError,
)
from app.domain.value_objects import CompanyId, PlanExecutionId


@dataclass
class PlanExecution:
    """Entidad que representa la ejecución de un plan de mantenimiento.

    Vincula un plan de mantenimiento con una orden de trabajo existente,
    registrando la fecha de ejecución y observaciones.
    """

    id: PlanExecutionId
    empresa_id: CompanyId
    plan_id: uuid.UUID
    work_order_id: uuid.UUID
    execution_date: datetime
    observations: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        plan_id: uuid.UUID,
        work_order_id: uuid.UUID,
        execution_date: datetime | None = None,
        observations: str | None = None,
    ) -> "PlanExecution":
        """Crea una nueva ejecución de plan de mantenimiento.

        Args:
            empresa_id: Empresa propietaria.
            plan_id: ID del plan de mantenimiento ejecutado.
            work_order_id: ID de la orden de trabajo asociada.
            execution_date: Fecha de ejecución (por defecto ahora).
            observations: Observaciones opcionales.

        Returns:
            Nueva entidad PlanExecution.

        Raises:
            PlanExecutionObservationsEmptyError: Si observations son solo espacios.
        """
        # ponytail: uuid4 asume colisión despreciable en single-node.
        if observations is not None and not observations.strip():
            raise PlanExecutionObservationsEmptyError()

        return cls(
            id=PlanExecutionId(uuid.uuid4()),
            empresa_id=empresa_id,
            plan_id=plan_id,
            work_order_id=work_order_id,
            execution_date=execution_date or datetime.now(),
            observations=observations.strip() if observations else None,
        )
