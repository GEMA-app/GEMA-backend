"""Caso de Uso para listar los movimientos de inventario de un repuesto."""

from app.application.dtos.inventory_part_dtos import InventoryEntryResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InventoryPartNotFoundError
from app.domain.value_objects import CompanyId, SparePartId


class ListInventoryEntriesUseCase:
    """Obtiene el historial paginado de movimientos de un repuesto específico."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, part_id_str: str, limit: int = 20, offset: int = 0
    ) -> list[InventoryEntryResponse]:
        """Obtiene y mapea los movimientos de inventario de un repuesto."""
        company_id = CompanyId.from_string(company_id_str)
        part_id = SparePartId.from_string(part_id_str)

        async with self.uow:
            # Validar que el repuesto existe en la empresa
            part = await self.uow.inventory_parts.get_by_id(part_id, company_id)
            if not part:
                raise InventoryPartNotFoundError(
                    f"El repuesto con ID '{part_id_str}' no existe en esta empresa."
                )

            entries = await self.uow.inventory_entries.get_all_by_repuesto(
                repuesto_id=part_id.value, empresa_id=company_id, limit=limit, offset=offset
            )

            return [
                InventoryEntryResponse(
                    id=str(e.id),
                    empresa_id=str(e.empresa_id),
                    repuesto_id=str(e.repuesto_id),
                    movement_type=e.tipo_movimiento,
                    quantity=e.cantidad,
                    work_order_id=str(e.ordenes_trabajo_id) if e.ordenes_trabajo_id else None,
                    usuario_id=str(e.usuario_id) if e.usuario_id else None,
                    precio_unitario=e.precio_unitario,
                    moneda=e.moneda,
                    fecha_movimiento=e.fecha_movimiento.isoformat() if e.fecha_movimiento else None,
                    reason=e.observaciones,
                )
                for e in entries
            ]
