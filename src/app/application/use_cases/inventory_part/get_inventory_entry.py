"""Caso de Uso para obtener un movimiento de inventario por su ID."""

from uuid import UUID

from app.application.dtos.inventory_part_dtos import InventoryEntryResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InventoryEntryNotFoundError
from app.domain.value_objects import CompanyId


class GetInventoryEntryUseCase:
    """Busca y recupera la información detallada de un movimiento de stock."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, entry_id_str: str) -> InventoryEntryResponse:
        """Busca el movimiento en el repositorio bajo aislamiento multi-tenant."""
        company_id = CompanyId.from_string(company_id_str)
        entry_id = UUID(entry_id_str)

        async with self.uow:
            entry = await self.uow.inventory_entries.get_by_id(entry_id, company_id)
            if not entry:
                raise InventoryEntryNotFoundError(
                    f"El movimiento con ID '{entry_id_str}' no existe en esta empresa."
                )

            return InventoryEntryResponse(
                id=str(entry.id),
                empresa_id=str(entry.empresa_id),
                repuesto_id=str(entry.repuesto_id),
                movement_type=entry.tipo_movimiento,
                quantity=entry.cantidad,
                work_order_id=str(entry.ordenes_trabajo_id) if entry.ordenes_trabajo_id else None,
                usuario_id=str(entry.usuario_id) if entry.usuario_id else None,
                precio_unitario=entry.precio_unitario,
                moneda=entry.moneda,
                fecha_movimiento=entry.fecha_movimiento.isoformat()
                if entry.fecha_movimiento
                else None,
                reason=entry.observaciones,
            )
