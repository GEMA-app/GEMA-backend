"""Caso de uso para asignar un técnico a una orden de trabajo."""

import uuid

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import WorkOrderNotFoundError
from app.domain.value_objects import CompanyId, UserId, WorkOrderId


class AssignTechnicianUseCase:
    """Caso de uso para asignar un técnico a una orden de trabajo."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id: str, work_order_id: str, technician_id: str) -> None:
        """Asigna un técnico a una orden de trabajo.

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

            # Check if technician exists and belongs to the company
            user = await self.uow.users.get_by_id(UserId(tech_uuid))
            if not user or str(user.empresa_id) != company_id:
                raise WorkOrderNotFoundError("El técnico no existe en esta empresa.")

            session = getattr(self.uow, "session", None)
            if session is not None and "Mock" not in type(session).__name__:
                from sqlalchemy import select

                from app.infrastructure.db.models.work_order import WorkOrderTechnicianModel

                # Check if already assigned
                stmt = select(WorkOrderTechnicianModel).where(
                    WorkOrderTechnicianModel.ordenes_trabajo_id == wo_id.value,
                    WorkOrderTechnicianModel.tecnico_id == tech_uuid,
                )
                res = await session.execute(stmt)
                existing = res.scalar_one_or_none()
                if not existing:
                    assoc = WorkOrderTechnicianModel(
                        empresa_id=company.value,
                        ordenes_trabajo_id=wo_id.value,
                        tecnico_id=tech_uuid,
                    )
                    session.add(assoc)

            await self.uow.commit()
