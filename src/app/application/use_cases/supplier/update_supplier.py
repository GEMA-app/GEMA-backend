"""Caso de uso para actualizar un proveedor existente."""

from uuid import UUID

from app.application.dtos.supplier_dtos import SupplierResponse, UpdateSupplierRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import SupplierNotFoundError, SupplierRifExistsError
from app.domain.value_objects import CompanyId


class UpdateSupplierUseCase:
    """Actualiza los datos de un proveedor validando unicidad de RIF."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        empresa_id_str: str,
        supplier_id: UUID,
        request: UpdateSupplierRequest,
    ) -> SupplierResponse:
        """Ejecuta la actualización de un proveedor.

        Args:
            empresa_id_str: UUID de la empresa como string.
            supplier_id: UUID del proveedor a actualizar.
            request: DTO con los campos a actualizar.

        Returns:
            DTO con los datos del proveedor actualizado.

        Raises:
            SupplierNotFoundError: Si no se encuentra el proveedor.
            SupplierRifExistsError: Si el nuevo RIF ya está en uso.
        """
        company_id = CompanyId.from_string(empresa_id_str)
        async with self.uow:
            supplier = await self.uow.suppliers.get_by_id(supplier_id, company_id.value)
            if not supplier:
                raise SupplierNotFoundError("Proveedor no encontrado.")

            if (
                "rif" in request._fields_set
                and request.rif is not None
                and request.rif != supplier.rif
            ):
                existing = await self.uow.suppliers.get_by_rif(request.rif, company_id.value)
                if existing:
                    raise SupplierRifExistsError(f"El RIF '{request.rif}' ya está en uso.")

            supplier.update(
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
