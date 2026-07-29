"""Caso de uso para eliminar una orden de trabajo."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.events import WorkOrderDeleted
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, WorkOrderId


class DeleteWorkOrderUseCase:
    """Caso de uso para eliminar una orden de trabajo por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id: str, work_order_id: str) -> None:
        """Ejecuta la eliminación de una orden de trabajo.

        Args:
            company_id: Identificador de la empresa.
            work_order_id: Identificador de la orden a eliminar.

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
            await self.uow.work_orders.delete(wo_id, company)

            self.uow.add_event(
                WorkOrderDeleted(
                    work_order_id=work_order_id,
                    empresa_id=str(company),
                )
            )
            await self.uow.commit()
