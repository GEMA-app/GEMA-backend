"""Caso de uso para crear un proveedor."""

import uuid

from app.application.dtos.supplier_dtos import CreateSupplierRequest, SupplierResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.supplier import Supplier
from app.domain.exceptions import SupplierRifExistsError
from app.domain.value_objects import CompanyId


class CreateSupplierUseCase:
    """Crea un nuevo proveedor en la empresa validando unicidad de RIF."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, empresa_id_str: str, request: CreateSupplierRequest
    ) -> SupplierResponse:
        """Ejecuta la creación de un proveedor.

        Args:
            empresa_id_str: UUID de la empresa como string.
            request: DTO con los datos del proveedor.

        Returns:
            DTO con los datos del proveedor creado.

        Raises:
            SupplierRifExistsError: Si ya existe un proveedor con el mismo RIF
                en la empresa.
        """
        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            if request.rif:
                existing = await self.uow.suppliers.get_by_rif(request.rif, company_id.value)
                if existing:
                    raise SupplierRifExistsError(f"El RIF '{request.rif}' ya está registrado.")
            supplier = Supplier.create(
                id=uuid.uuid4(),
                empresa_id=company_id.value,
                name=request.name,
                rif=request.rif,
                phone=request.phone,
                email=request.email,
                contact=request.contact,
            )
            await self.uow.suppliers.save(supplier)
            await self.uow.commit()
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
