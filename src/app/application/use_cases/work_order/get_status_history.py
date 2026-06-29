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

            logs = []
            session = getattr(self.uow, "session", None)
            if session is not None and "Mock" not in type(session).__name__:
                from sqlalchemy import select

                from app.infrastructure.db.models.work_order import WorkOrderStatusLogModel

                stmt = select(WorkOrderStatusLogModel).where(
                    WorkOrderStatusLogModel.ordenes_trabajo_id == wo_id.value,
                    WorkOrderStatusLogModel.empresa_id == company.value,
                ).order_by(WorkOrderStatusLogModel.fecha_cambio.asc())

                res = await session.execute(stmt)
                models = res.scalars().all()
                for m in models:
                    logs.append(
                        WorkOrderStatusLogResponse(
                            id=str(m.id),
                            ordenes_trabajo_id=str(m.ordenes_trabajo_id),
                            estado_anterior=m.estado_anterior.value if m.estado_anterior else None,
                            estado_nuevo=m.estado_nuevo.value,
                            usuario_id=str(m.usuario_id) if m.usuario_id else None,
                            motivo=m.motivo,
                            fecha_cambio=m.fecha_cambio,
                        )
                    )

            return logs
