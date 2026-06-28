"""Caso de uso para obtener una orden de trabajo por su ID."""

from app.application.dtos.work_order_dtos import WorkOrderResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, WorkOrderId


class GetWorkOrderUseCase:
    """Caso de uso para obtener una orden de trabajo por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id: str, work_order_id: str
    ) -> WorkOrderResponse:
        """Ejecuta la obtención de una orden de trabajo.

        Args:
            company_id: Identificador de la empresa.
            work_order_id: Identificador de la orden.

        Returns:
            WorkOrderResponse: DTO con los datos de la orden.

        Raises:
            WorkOrderNotFoundError: Si la orden no existe.
        """
        company = CompanyId.from_string(company_id)
        wo_id = WorkOrderId.from_string(work_order_id)

        async with self.uow:
            wo = await self.uow.work_orders.get_by_id(wo_id, company)
            if not wo:
                raise WorkOrderNotFoundError(
                    f"Orden de trabajo con ID '{work_order_id}' no encontrada."
                )
            return WorkOrderResponse.from_entity(wo)
