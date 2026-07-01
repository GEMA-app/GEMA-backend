"""Caso de uso para obtener un proveedor por ID."""

from uuid import UUID

from app.application.dtos.supplier_dtos import SupplierResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import SupplierNotFoundError
from app.domain.value_objects import CompanyId


class GetSupplierUseCase:
    """Obtiene un proveedor por su ID dentro del tenant."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str, supplier_id: UUID
    ) -> SupplierResponse:
        """Ejecuta la obtención de un proveedor por ID.

        Args:
            empresa_id_str: UUID de la empresa como string.
            supplier_id: UUID del proveedor a buscar.

        Returns:
            DTO con los datos del proveedor encontrado.

        Raises:
            SupplierNotFoundError: Si no se encuentra el proveedor.
        """
        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            supplier = await self.uow.suppliers.get_by_id(
                supplier_id, company_id.value
            )
            if not supplier:
                raise SupplierNotFoundError("Proveedor no encontrado.")
            return SupplierResponse(
                id=supplier.id,
                empresa_id=supplier.empresa_id,
                name=supplier.name,
                rif=supplier.rif,
                phone=supplier.phone,
                email=supplier.email,
                contact=supplier.contact,
                version=supplier.version,
                created_at=supplier.created_at,
                updated_at=supplier.updated_at,
            )
