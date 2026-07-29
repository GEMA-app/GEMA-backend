"""Caso de uso para remover un técnico de una orden de trabajo."""

import uuid

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.events import WorkOrderUpdated
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, UserId, WorkOrderId


class RemoveTechnicianUseCase:
    """Caso de uso para remover un técnico de una orden de trabajo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id: str, work_order_id: str, technician_id: str) -> None:
        """Remueve un técnico de una orden de trabajo.

        Args:
            company_id: Identificador de la empresa.
            work_order_id: Identificador de la orden de trabajo.
            technician_id: Identificador del técnico.
        """
        company = CompanyId.from_string(company_id)
        wo_id = WorkOrderId.from_string(work_order_id)
        tech_uuid = uuid.UUID(technician_id)

        async with self.uow:
            wo = await self.uow.work_orders.get_by_id(wo_id, company)
            if not wo:
                raise WorkOrderNotFoundError(
                    f"Orden de trabajo con ID '{work_order_id}' no encontrada."
                )

            await self.uow.work_orders.remove_technician(wo_id, UserId(tech_uuid), company)

            self.uow.add_event(
                WorkOrderUpdated(
                    work_order_id=work_order_id,
                    empresa_id=str(company),
                )
            )
            await self.uow.commit()
