"""Caso de Uso para eliminar un repuesto del inventario."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import InvalidStockError, InventoryPartNotFoundError
from app.domain.value_objects import CompanyId, RepuestoId


class DeleteInventoryPartUseCase:
    """Elimina un repuesto del inventario de la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, part_id_str: str) -> None:
        """Elimina el repuesto validando stock actual y existencia de movimientos."""
        company_id = CompanyId.from_string(company_id_str)
        part_id = RepuestoId.from_string(part_id_str)

        async with self.uow:
            inventory_part = await self.uow.inventory_parts.get_by_id(part_id, company_id)
            if not inventory_part:
                raise InventoryPartNotFoundError(
                    f"El repuesto con ID '{part_id_str}' no existe en esta empresa."
                )

            # Validar stock_actual == 0
            if inventory_part.stock_actual > 0:
                raise InvalidStockError(
                    f"No se puede eliminar un repuesto con stock mayor a cero. "
                    f"Stock actual: {inventory_part.stock_actual}."
                )

            # Validar si tiene movimientos históricos
            movements = await self.uow.inventory_entries.get_all_by_repuesto(
                repuesto_id=part_id.value, empresa_id=company_id, limit=1
            )
            if movements:
                raise InvalidStockError(
                    "No se puede eliminar un repuesto que tiene movimientos "
                    "de inventario registrados."
                )

            await self.uow.inventory_parts.delete(part_id, company_id)
            await self.uow.commit()

