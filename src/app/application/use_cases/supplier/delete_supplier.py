"""Caso de uso para eliminar un proveedor."""

from uuid import UUID

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import SupplierHasInventoryPartsError, SupplierNotFoundError
from app.domain.value_objects import CompanyId


class DeleteSupplierUseCase:
    """Elimina un proveedor por su ID si no tiene repuestos asociados."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str, supplier_id: UUID
    ) -> None:
        """Ejecuta la eliminación de un proveedor.

        Args:
            empresa_id_str: UUID de la empresa como string.
            supplier_id: UUID del proveedor a eliminar.

        Raises:
            SupplierNotFoundError: Si no se encuentra el proveedor.
            SupplierHasInventoryPartsError: Si el proveedor tiene repuestos asociados.
        """
        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            supplier = await self.uow.suppliers.get_by_id(
                supplier_id, company_id.value
            )
            if not supplier:
                raise SupplierNotFoundError("Proveedor no encontrado.")

            # Verificar si tiene repuestos de inventario asociados
            has_parts = await self.uow.suppliers.has_inventory_parts(
                supplier_id, company_id.value
            )
            if has_parts:
                raise SupplierHasInventoryPartsError(
                    "No se puede eliminar un proveedor con repuestos de inventario asociados."
                )

            await self.uow.suppliers.delete(supplier.id, company_id.value)
            await self.uow.commit()
