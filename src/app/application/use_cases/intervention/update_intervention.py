"""Caso de uso para actualizar una intervención técnica."""

from app.application.dtos.intervention_dtos import (
    InterventionResponse,
    UpdateInterventionRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.intervention import InterventionNotFoundError
from app.domain.value_objects.identifier import CompanyId, InterventionId


class UpdateInterventionUseCase:
    """Caso de uso para actualizar una intervención técnica existente."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(
        self, ot_id: str, intervention_id: str, empresa_id: str, request: UpdateInterventionRequest
    ) -> InterventionResponse:
        """Ejecuta el caso de uso para actualizar una intervención técnica.

        Args:
            ot_id: Identificador UUID de la orden de trabajo (desde el path).
            intervention_id: Identificador UUID de la intervención.
            empresa_id: Identificador UUID de la empresa.
            request: DTO con los campos a actualizar.

        Returns:
            InterventionResponse con los datos de la intervención actualizada.

        Raises:
            InterventionNotFoundError: Si la intervención no existe.
        """
        intervention_id_internal = InterventionId.from_string(intervention_id)
        company_id = CompanyId.from_string(empresa_id)

        async with self._uow:
            intervention = await self._uow.interventions.get_by_id(
                intervention_id_internal, company_id
            )

            if intervention is None:
                raise InterventionNotFoundError(f"Intervención {intervention_id} no encontrada")

            # La entidad es frozen, se recrea con replace (importado desde dataclasses)
            from dataclasses import replace

            updated_intervention = replace(
                intervention,
                tareas_realizadas=request.tareas_realizadas or intervention.tareas_realizadas,
                horas_hombre=request.horas_hombre or intervention.horas_hombre,
            )

            await self._uow.interventions.save(updated_intervention)
            await self._uow.commit()

            return InterventionResponse(
                id=updated_intervention.id.value,
                empresa_id=updated_intervention.empresa_id.value,
                work_order_id=updated_intervention.work_order_id.value,
                technician_id=updated_intervention.technician_id.value,
                tareas_realizadas=updated_intervention.tareas_realizadas,
                fecha_inicio=updated_intervention.fecha_inicio,
                fecha_fin=updated_intervention.fecha_fin,
                horas_hombre=updated_intervention.horas_hombre,
            )
