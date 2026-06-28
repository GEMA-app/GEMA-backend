"""Caso de uso para obtener una intervención técnica por ID."""

from app.application.dtos.intervention_dtos import InterventionResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.intervention import InterventionNotFoundError
from app.domain.value_objects.identifier import CompanyId, InterventionId


class GetInterventionUseCase:
    """Caso de uso para obtener una intervención técnica por ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(
        self, ot_id: str, intervention_id: str, empresa_id: str
    ) -> InterventionResponse:
        """Ejecuta el caso de uso para obtener una intervención por ID.

        Args:
            ot_id: Identificador UUID de la orden de trabajo (desde el path).
            intervention_id: Identificador UUID de la intervención.
            empresa_id: Identificador UUID de la empresa.

        Returns:
            InterventionResponse con los datos de la intervención encontrada.

        Raises:
            InterventionNotFoundError: Si no existe la intervención con el ID
                proporcionado en la empresa especificada.
        """
        intervention_id_internal = InterventionId.from_string(intervention_id)
        company_id = CompanyId.from_string(empresa_id)

        async with self._uow:
            intervention = await self._uow.interventions.get_by_id(
                intervention_id_internal, company_id
            )

        if intervention is None:
            raise InterventionNotFoundError(f"Intervención {intervention_id} no encontrada")

        return InterventionResponse(
            id=intervention.id.value,
            empresa_id=intervention.empresa_id.value,
            work_order_id=intervention.work_order_id.value,
            technician_id=intervention.technician_id.value,
            tareas_realizadas=intervention.tareas_realizadas,
            fecha_inicio=intervention.fecha_inicio,
            fecha_fin=intervention.fecha_fin,
            horas_hombre=intervention.horas_hombre,
        )
