"""Caso de Uso para obtener un repuesto por su ID."""

from app.application.dtos.inventory_part_dtos import InventoryPartResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InventoryPartNotFoundError
from app.domain.value_objects import CompanyId, SparePartId


class GetInventoryPartUseCase:
    """Recupera la información de un repuesto específico de manera aislada."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, part_id_str: str) -> InventoryPartResponse:
        """Busca el repuesto dentro del contexto transaccional multi-tenant."""
        company_id = CompanyId.from_string(company_id_str)
        part_id = SparePartId.from_string(part_id_str)

        async with self.uow:
            inventory_part = await self.uow.inventory_parts.get_by_id(part_id, company_id)
            if not inventory_part:
                raise InventoryPartNotFoundError(
                    f"El repuesto con ID '{part_id_str}' no existe en esta empresa."
                )

            return InventoryPartResponse(
                id=str(inventory_part.id),
                empresa_id=str(inventory_part.empresa_id),
                articulo_id=str(inventory_part.articulo_id),
                proveedor_id=str(inventory_part.proveedor_id),
                stock_actual=inventory_part.stock_actual,
                stock_minimo=inventory_part.stock_minimo,
                ubicacion_almacen=inventory_part.ubicacion_almacen,
                precio_unitario=inventory_part.precio_unitario,
                moneda=inventory_part.moneda,
                version=inventory_part.version,
            )
