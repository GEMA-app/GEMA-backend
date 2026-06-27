"""Caso de uso: GetPlanExecution — obtener detalle de una ejecución de plan."""

from app.application.dtos.plan_execution_dtos import PlanExecutionResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.plan_execution import PlanExecutionNotFoundError
from app.domain.value_objects import CompanyId, PlanExecutionId


class GetPlanExecutionUseCase:
    """Caso de uso para obtener una ejecución de plan por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, execution_id_str: str
    ) -> PlanExecutionResponse:
        """Obtiene una ejecución de plan por su ID.

        Args:
            company_id_str: ID de la empresa como string.
            execution_id_str: ID de la ejecución como string.

        Returns:
            PlanExecutionResponse con los datos de la ejecución.

        Raises:
            PlanExecutionNotFoundError: Si no existe la ejecución.
        """
        company_id = CompanyId.from_string(company_id_str)
        exec_id = PlanExecutionId.from_string(execution_id_str)

        async with self.uow:
            execution = await self.uow.plan_executions.get_by_id(
                exec_id, company_id
            )
            if not execution:
                raise PlanExecutionNotFoundError(execution_id_str, company_id_str)

            return PlanExecutionResponse(
                id=str(execution.id),
                empresa_id=str(execution.empresa_id),
                plan_id=str(execution.plan_id),
                work_order_id=str(execution.work_order_id) if execution.work_order_id else None,
                execution_date=execution.execution_date,
                observations=execution.observations,
                created_at=execution.created_at,
                updated_at=execution.updated_at,
            )
