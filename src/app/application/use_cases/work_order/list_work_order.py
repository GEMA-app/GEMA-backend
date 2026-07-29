"""Caso de uso para listar órdenes de trabajo de una empresa."""

from app.application.dtos.work_order_dtos import WorkOrderResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import AssetId, CompanyId


class ListWorkOrdersUseCase:
    """Caso de uso para listar órdenes de trabajo con filtros opcionales."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id: str,
        estado: str | None = None,
        activo_id: str | None = None,
        tipo: str | None = None,
        supervisor_id: str | None = None,
        tecnico_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[WorkOrderResponse], int]:
        """Ejecuta el listado de órdenes de trabajo.

        Args:
            company_id: Identificador de la empresa.
            estado: Filtrar por estado (opcional).
            activo_id: Filtrar por activo (opcional).
            tipo: Filtrar por tipo (opcional).
            supervisor_id: Filtrar por supervisor (opcional).
            tecnico_id: Filtrar por técnico asignado (opcional).
            offset: Desplazamiento.
            limit: Límite.

        Returns:
            tuple: Lista de DTOs y el total de resultados.
        """
        company = CompanyId.from_string(company_id)
        asset_id = AssetId.from_string(activo_id) if activo_id else None

        async with self.uow:
            work_orders, total = await self.uow.work_orders.list_by_company(
                company,
                estado=estado,
                activo_id=asset_id,
                tipo=tipo,
                supervisor_id=supervisor_id,
                tecnico_id=tecnico_id,
                offset=offset,
                limit=limit,
            )

        return [WorkOrderResponse.from_entity(wo) for wo in work_orders], total
