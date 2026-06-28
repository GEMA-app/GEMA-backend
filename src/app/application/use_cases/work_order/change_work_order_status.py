"""Caso de uso para cambiar el estado de una orden de trabajo."""

from app.application.dtos.work_order_dtos import (
    ChangeWorkOrderStatusRequest,
    WorkOrderResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import WorkOrderStatus
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, WorkOrderId


class ChangeWorkOrderStatusUseCase:
    """Caso de uso para cambiar el estado de una orden de trabajo.

    Utiliza la máquina de estados de la entidad WorkOrder para validar
    y ejecutar la transición (start/pause/resume/close/cancel).
    """

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id: str,
        work_order_id: str,
        request: ChangeWorkOrderStatusRequest,
    ) -> WorkOrderResponse:
        """Ejecuta el cambio de estado de una orden de trabajo.

        Args:
            company_id: Identificador de la empresa.
            work_order_id: Identificador de la orden.
            request: DTO con el nuevo estado solicitado.

        Returns:
            WorkOrderResponse: DTO con los datos actualizados.

        Raises:
            WorkOrderNotFoundError: Si la orden no existe.
            WorkOrderInvalidStateError: Si la transición no es válida.
        """
        company = CompanyId.from_string(company_id)
        wo_id = WorkOrderId.from_string(work_order_id)
        new_status = WorkOrderStatus(request.estado)

        async with self.uow:
            wo = await self.uow.work_orders.get_by_id(wo_id, company)
            if not wo:
                raise WorkOrderNotFoundError(
                    f"Orden de trabajo con ID '{work_order_id}' no encontrada."
                )

            if new_status == WorkOrderStatus.IN_PROGRESS:
                wo.start()
            elif new_status == WorkOrderStatus.PAUSED:
                wo.pause()
            elif new_status == WorkOrderStatus.CLOSED:
                wo.close()
            elif new_status == WorkOrderStatus.CANCELLED:
                wo.cancel()

            await self.uow.work_orders.save(wo)
            await self.uow.commit()

        return WorkOrderResponse.from_entity(wo)
