"""Caso de uso para crear una intervención técnica."""


from app.application.dtos.intervention_dtos import CreateInterventionRequest, InterventionResponse
from app.application.ports.intervention_repository import InterventionRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.intervention import TechnicalIntervention
from app.domain.value_objects.identifier import UserId, WorkOrderId


class CreateInterventionUseCase:
    """Caso de uso para crear una nueva intervención técnica."""

    def __init__(
        self,
        uow: UnitOfWorkPort,
        intervention_repository: InterventionRepositoryPort,
    ) -> None:
        self._uow = uow
        self._intervention_repository = intervention_repository

    async def execute(self, ot_id: str, request: CreateInterventionRequest) -> InterventionResponse:
        """Ejecuta el caso de uso para crear una intervención técnica.

        Crea la entidad de dominio y la persiste a través del Unit of Work.

        Args:
            ot_id: Identificador UUID de la orden de trabajo.
            request: DTO con los datos para crear la intervención.

        Returns:
            InterventionResponse con los datos de la intervención creada.
        """
        intervention = TechnicalIntervention.create(
            work_order_id=WorkOrderId.from_string(ot_id),
            technician_id=UserId.from_string(str(request.technician_id)),
            tareas_realizadas=request.tareas_realizadas,
            fecha_inicio=request.fecha_inicio,
            horas_hombre=request.horas_hombre,
        )

        async with self._uow:
            await self._intervention_repository.save(intervention)
            await self._uow.commit()

        return InterventionResponse(
            id=intervention.id.value,
            work_order_id=intervention.work_order_id.value,
            technician_id=intervention.technician_id.value,
            tareas_realizadas=intervention.tareas_realizadas,
            fecha_inicio=intervention.fecha_inicio,
            fecha_fin=intervention.fecha_fin,
            horas_hombre=intervention.horas_hombre,
        )
