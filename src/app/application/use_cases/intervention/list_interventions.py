"""Caso de uso para listar intervenciones técnicas."""

from app.application.dtos.intervention_dtos import InterventionResponse
from app.application.ports.intervention_repository import InterventionRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects.identifier import CompanyId, WorkOrderId


class ListInterventionsUseCase:
    """Caso de uso para listar intervenciones técnicas de una orden de trabajo."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        intervention_repository: InterventionRepositoryPort,
    ) -> None:
        self._uow = uow
        self._intervention_repository = intervention_repository

    async def execute(
        self, ot_id: str, empresa_id: str, offset: int = 0, limit: int = 100
    ) -> tuple[list[InterventionResponse], int]:
        """Ejecuta el caso de uso para listar intervenciones de una orden de trabajo.

        Args:
            ot_id: Identificador UUID de la orden de trabajo.
            empresa_id: Identificador UUID de la empresa.
            offset: Número de registros a omitir (paginación).
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Una tupla con la lista de InterventionResponse y el total de registros.
        """
        company_id = CompanyId.from_string(empresa_id)
        work_order_id = WorkOrderId.from_string(ot_id)

        async with self._uow:
            interventions = await self._intervention_repository.get_by_work_order(
                work_order_id=work_order_id,
                empresa_id=company_id,
            )

        return [
            InterventionResponse(
                id=i.id.value,
                work_order_id=i.work_order_id.value,
                technician_id=i.technician_id.value,
                tareas_realizadas=i.tareas_realizadas,
                fecha_inicio=i.fecha_inicio,
                fecha_fin=i.fecha_fin,
                horas_hombre=i.horas_hombre,
            )
            for i in interventions
        ], len(interventions)
