"""Caso de uso para actualizar una orden de trabajo existente."""

from app.application.dtos.work_order_dtos import (
    UpdateWorkOrderRequest,
    WorkOrderResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, UserId, WorkOrderId


class UpdateWorkOrderUseCase:
    """Caso de uso para actualizar los detalles de una orden de trabajo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id: str,
        work_order_id: str,
        request: UpdateWorkOrderRequest,
    ) -> WorkOrderResponse:
        """Ejecuta la actualización de una orden de trabajo.

        Args:
            company_id: Identificador de la empresa.
            work_order_id: Identificador de la orden a actualizar.
            request: DTO con los campos a actualizar.

        Returns:
            WorkOrderResponse: DTO con los datos actualizados.

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

            supervisor = (
                UserId.from_string(request.supervisor_id)
                if request.supervisor_id
                else None
            )
            wo.update_details(
                descripcion_trabajo=request.descripcion_trabajo,
                costo_estimado=request.costo_estimado,
                costo_real=request.costo_real,
                supervisor_id=supervisor,
            )

            await self.uow.work_orders.save(wo)
            await self.uow.commit()

        return WorkOrderResponse.from_entity(wo)
