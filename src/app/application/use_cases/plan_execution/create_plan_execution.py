"""Caso de uso: CreatePlanExecution — registrar una ejecución de plan de mantenimiento."""

from app.application.dtos.plan_execution_dtos import (
    PlanExecutionCreateRequest,
    PlanExecutionResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.plan_execution import PlanExecution
from app.domain.value_objects import CompanyId


class CreatePlanExecutionUseCase:
    """Caso de uso para registrar una nueva ejecución de plan de mantenimiento."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: PlanExecutionCreateRequest
    ) -> PlanExecutionResponse:
        """Ejecuta el caso de uso.

        Args:
            company_id_str: ID de la empresa como string.
            request: DTO con los datos de creación.

        Returns:
            PlanExecutionResponse con los datos de la ejecución creada.
        """
        company_id = CompanyId.from_string(company_id_str)

        execution = PlanExecution.create(
            empresa_id=company_id,
            plan_id=request.plan_id,
            work_order_id=request.work_order_id,
            execution_date=request.execution_date,
            observations=request.observations,
        )

        async with self.uow:
            saved = await self.uow.plan_executions.save(execution)
            await self.uow.commit()

        return self._to_response(saved)

    @staticmethod
    def _to_response(entity: PlanExecution) -> PlanExecutionResponse:
        """Convierte la entidad a DTO de respuesta."""
        return PlanExecutionResponse(
            id=str(entity.id),
            empresa_id=str(entity.empresa_id),
            plan_id=str(entity.plan_id),
            work_order_id=str(entity.work_order_id) if entity.work_order_id else None,
            execution_date=entity.execution_date,
            observations=entity.observations,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
