"""Endpoints REST para el CRUD de proveedores.

Ruta base: /v1/empresas/{empresa_id}/proveedores
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.supplier_dtos import (
    CreateSupplierRequest as CreateSupplierDTO,
)
from app.application.dtos.supplier_dtos import (
    SupplierResponse,
)
from app.application.dtos.supplier_dtos import (
    UpdateSupplierRequest as UpdateSupplierDTO,
)
from app.application.use_cases.supplier.create_supplier import CreateSupplierUseCase
from app.application.use_cases.supplier.delete_supplier import DeleteSupplierUseCase
from app.application.use_cases.supplier.get_supplier import GetSupplierUseCase
from app.application.use_cases.supplier.list_suppliers import ListSuppliersUseCase
from app.application.use_cases.supplier.update_supplier import UpdateSupplierUseCase
from app.composition.container.supplier import (
    get_create_supplier_use_case,
    get_delete_supplier_use_case,
    get_get_supplier_use_case,
    get_list_suppliers_use_case,
    get_update_supplier_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_dual_permission,
)
from app.presentation.api.v1.schemas.supplier import (
    CreateSupplierRequest,
    SupplierAttributes,
    SupplierDocument,
    SupplierListDocument,
    SupplierResource,
    UpdateSupplierRequest,
)

router = APIRouter()


def _build_resource(supplier: "SupplierResponse") -> SupplierResource:
    """Construye un recurso JSON:API a partir de un DTO de proveedor.

    Args:
        supplier: DTO con los datos del proveedor.

    Returns:
        Recurso JSON:API formateado.
    """
    return SupplierResource(
        id=str(supplier.id),
        attributes=SupplierAttributes(
            empresa_id=str(supplier.empresa_id),
            name=supplier.name,
            rif=supplier.rif,
            phone=supplier.phone,
            email=supplier.email,
            contact=supplier.contact,
            version=supplier.version,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
        ),
    )


def _build_document(supplier: "SupplierResponse") -> SupplierDocument:
    """Construye un documento JSON:API a partir de un DTO de proveedor."""
    return SupplierDocument(data=_build_resource(supplier))


@router.post("", response_model=SupplierDocument, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    empresa_id: str,
    payload: CreateSupplierRequest,
    use_case: CreateSupplierUseCase = Depends(get_create_supplier_use_case),
    current_user: UserResponse = Depends(
        require_dual_permission(
            PermissionModule.INVENTORY, "create", PermissionModule.ADMIN, "create"
        )
    ),
) -> SupplierDocument:
    """Crea un nuevo proveedor en la empresa.

    Valida que el RIF sea único dentro del tenant.
    """
    dto = CreateSupplierDTO(
        name=payload.data.attributes.name,
        rif=payload.data.attributes.rif,
        phone=payload.data.attributes.phone,
        email=payload.data.attributes.email,
        contact=payload.data.attributes.contact,
    )
    supplier = await use_case.execute(empresa_id, dto)
    return _build_document(supplier)


@router.get("", response_model=SupplierListDocument)
async def list_suppliers(
    empresa_id: str,
    search: str | None = Query(None, description="Búsqueda por nombre o RIF"),
    use_case: ListSuppliersUseCase = Depends(get_list_suppliers_use_case),
    current_user: UserResponse = Depends(
        require_dual_permission(PermissionModule.INVENTORY, "view", PermissionModule.ADMIN, "view")
    ),
) -> SupplierListDocument:
    """Lista los proveedores de la empresa.

    Soporta búsqueda opcional por nombre o RIF.
    """
    suppliers = await use_case.execute(empresa_id, search=search)
    return SupplierListDocument(
        data=[_build_resource(s) for s in suppliers],
    )


@router.get("/{supplier_id}", response_model=SupplierDocument)
async def get_supplier(
    empresa_id: str,
    supplier_id: UUID,
    use_case: GetSupplierUseCase = Depends(get_get_supplier_use_case),
    current_user: UserResponse = Depends(
        require_dual_permission(PermissionModule.INVENTORY, "view", PermissionModule.ADMIN, "view")
    ),
) -> SupplierDocument:
    """Obtiene el detalle de un proveedor por ID."""
    supplier = await use_case.execute(empresa_id, supplier_id)
    return _build_document(supplier)


@router.patch("/{supplier_id}", response_model=SupplierDocument)
async def update_supplier(
    empresa_id: str,
    supplier_id: UUID,
    payload: UpdateSupplierRequest,
    use_case: UpdateSupplierUseCase = Depends(get_update_supplier_use_case),
    current_user: UserResponse = Depends(
        require_dual_permission(PermissionModule.INVENTORY, "edit", PermissionModule.ADMIN, "edit")
    ),
) -> SupplierDocument:
    """Actualiza los datos de un proveedor.

    Valida unicidad de RIF si se está actualizando ese campo.
    """
    attrs = payload.data.attributes
    dto = UpdateSupplierDTO(
        name=attrs.name,
        rif=attrs.rif,
        phone=attrs.phone,
        email=attrs.email,
        contact=attrs.contact,
        version=attrs.version,
    )
    supplier = await use_case.execute(empresa_id, supplier_id, dto)
    return _build_document(supplier)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    empresa_id: str,
    supplier_id: UUID,
    use_case: DeleteSupplierUseCase = Depends(get_delete_supplier_use_case),
    current_user: UserResponse = Depends(
        require_dual_permission(
            PermissionModule.INVENTORY, "delete", PermissionModule.ADMIN, "delete"
        )
    ),
) -> None:
    """Elimina un proveedor si no tiene repuestos de inventario asociados."""
    await use_case.execute(empresa_id, supplier_id)
