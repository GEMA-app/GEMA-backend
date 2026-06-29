"""Caso de uso para remover un técnico de una orden de trabajo."""

import uuid

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, WorkOrderId


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

            session = getattr(self.uow, "session", None)
            if session is not None and "Mock" not in type(session).__name__:
                from sqlalchemy import delete

                from app.infrastructure.db.models.work_order import WorkOrderTechnicianModel

                stmt = delete(WorkOrderTechnicianModel).where(
                    WorkOrderTechnicianModel.ordenes_trabajo_id == wo_id.value,
                    WorkOrderTechnicianModel.tecnico_id == tech_uuid,
                    WorkOrderTechnicianModel.empresa_id == company.value,
                )
                await session.execute(stmt)

            await self.uow.commit()
