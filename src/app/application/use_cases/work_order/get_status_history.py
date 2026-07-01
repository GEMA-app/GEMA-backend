"""Caso de uso para obtener el historial de estados de una orden de trabajo."""

from app.application.dtos.work_order_dtos import WorkOrderStatusLogResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, WorkOrderId


class GetWorkOrderStatusHistoryUseCase:
    """Caso de uso para obtener el historial de cambios de estado de una orden de trabajo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id: str, work_order_id: str
    ) -> list[WorkOrderStatusLogResponse]:
        """Obtiene la lista de cambios de estado de una OT.

        Args:
            company_id: Identificador de la empresa.
            work_order_id: Identificador de la orden de trabajo.
        """
        company = CompanyId.from_string(company_id)
        wo_id = WorkOrderId.from_string(work_order_id)

        async with self.uow:
            wo = await self.uow.work_orders.get_by_id(wo_id, company)
            if not wo:
                raise WorkOrderNotFoundError(
                    f"Orden de trabajo con ID '{work_order_id}' no encontrada."
                )

            logs = await self.uow.work_orders.get_status_history(wo_id, company)
            return logs
