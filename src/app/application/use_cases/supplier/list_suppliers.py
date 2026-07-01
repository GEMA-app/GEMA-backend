"""Caso de uso para listar proveedores."""

from app.application.dtos.supplier_dtos import SupplierResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListSuppliersUseCase:
    """Lista los proveedores de un tenant, con búsqueda opcional por nombre o RIF."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str, search: str | None = None
    ) -> list[SupplierResponse]:
        """Ejecuta la obtención de todos los proveedores de la empresa.

        Args:
            empresa_id_str: UUID de la empresa como string.
            search: Término opcional de búsqueda por nombre o RIF.

        Returns:
            Lista de DTOs con los datos de los proveedores encontrados.
        """
        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            suppliers = await self.uow.suppliers.get_all_by_company(
                company_id.value, search=search
            )
            return [
                SupplierResponse(
                    id=s.id,
                    empresa_id=s.empresa_id,
                    name=s.name,
                    rif=s.rif,
                    phone=s.phone,
                    email=s.email,
                    contact=s.contact,
                    version=s.version,
                    created_at=s.created_at,
                    updated_at=s.updated_at,
                )
                for s in suppliers
            ]
