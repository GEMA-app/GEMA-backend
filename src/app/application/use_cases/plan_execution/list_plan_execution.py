"""Caso de uso: ListPlanExecution — listar ejecuciones de un plan."""

from uuid import UUID

from app.application.dtos.plan_execution_dtos import (
    PlanExecutionListResponse,
    PlanExecutionResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListPlanExecutionUseCase:
    """Caso de uso para listar ejecuciones de un plan de mantenimiento."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, plan_id_str: str) -> PlanExecutionListResponse:
        """Lista ejecuciones de un plan.

        Args:
            company_id_str: ID de la empresa como string.
            plan_id_str: ID del plan de mantenimiento como string.

        Returns:
            PlanExecutionListResponse con la lista de ejecuciones.
        """
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            executions = await self.uow.plan_executions.list_by_plan_id(
                UUID(plan_id_str), company_id
            )
            data = [
                PlanExecutionResponse(
                    id=str(e.id),
                    empresa_id=str(e.empresa_id),
                    plan_id=str(e.plan_id),
                    work_order_id=str(e.work_order_id),
                    execution_date=e.execution_date,
                    observations=e.observations,
                    created_at=e.created_at,
                    updated_at=e.updated_at,
                )
                for e in executions
            ]
            return PlanExecutionListResponse(data=data, total=len(data))
