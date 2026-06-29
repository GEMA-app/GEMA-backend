"""Endpoints de la API REST para la gestión de repuestos de inventario (InventoryPart).

Cumple estrictamente con la especificación JSON:API de la plataforma GEMA.
"""

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.inventory_part_dtos import (
    CreateInventoryPartRequest as CreateInventoryPartDTO,
    UpdateInventoryPartRequest as UpdateInventoryPartDTO,
)
from app.application.use_cases.inventory_part.create_inventory_part import CreateInventoryPartUseCase
from app.application.use_cases.inventory_part.get_inventory_part import GetInventoryPartUseCase
from app.application.use_cases.inventory_part.list_inventory_parts import ListInventoryPartsUseCase
from app.application.use_cases.inventory_part.update_inventory_part import UpdateInventoryPartUseCase
from app.composition.container.inventory_part import (
    get_create_inventory_part_use_case,
    get_inventory_part_use_case,
    get_list_inventory_parts_use_case,
    get_update_inventory_part_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
    require_tenant_read,
)
from app.presentation.api.v1.schemas.inventory_part import (
    CreateInventoryPartRequest,
    InventoryPartAttributes,
    InventoryPartDocument,
    InventoryPartListDocument,
    InventoryPartResource,
    UpdateInventoryPartRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=InventoryPartDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un repuesto con stock inicial",
)
async def create_inventory_part(
    empresa_id: str,
    request: CreateInventoryPartRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "create")),
    use_case: CreateInventoryPartUseCase = Depends(get_create_inventory_part_use_case),
) -> InventoryPartDocument:
    """Crea un nuevo repuesto en el inventario asociado a la empresa.

    Garantiza el registro controlado de las existencias iniciales en almacén.
    """
    dto = CreateInventoryPartDTO(
        articulo_id=request.data.attributes.articulo_id,
        proveedor_id=request.data.attributes.proveedor_id,
        stock_minimo=request.data.attributes.stock_minimo,
        ubicacion_almacen=request.data.attributes.ubicacion_almacen,
        precio_unitario=request.data.attributes.precio_unitario,
        moneda=request.data.attributes.moneda,
        stock_actual=request.data.attributes.stock_actual,  # Stock inicial provisto por el DTO
    )
    res = await use_case.execute(empresa_id, dto)
    return InventoryPartDocument(
        data=InventoryPartResource(
            id=res.id,
            attributes=InventoryPartAttributes(
                empresa_id=res.empresa_id,
                articulo_id=res.articulo_id,
                proveedor_id=res.proveedor_id,
                stock_actual=res.stock_actual,
                stock_minimo=res.stock_minimo,
                ubicacion_almacen=res.ubicacion_almacen,
                precio_unitario=res.precio_unitario,
                moneda=res.moneda,
                version=res.version,
            ),
        )
    )


@router.get(
    "/{part_id}",
    response_model=InventoryPartDocument,
    summary="Obtener un repuesto por ID",
)
async def get_inventory_part(
    empresa_id: str,
    part_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetInventoryPartUseCase = Depends(get_inventory_part_use_case),
) -> InventoryPartDocument:
    """Obtiene los detalles informativos de un repuesto bajo aislamiento multi-tenant."""
    res = await use_case.execute(empresa_id, part_id)
    return InventoryPartDocument(
        data=InventoryPartResource(
            id=res.id,
            attributes=InventoryPartAttributes(
                empresa_id=res.empresa_id,
                articulo_id=res.articulo_id,
                proveedor_id=res.proveedor_id,
                stock_actual=res.stock_actual,
                stock_minimo=res.stock_minimo,
                ubicacion_almacen=res.ubicacion_almacen,
                precio_unitario=res.precio_unitario,
                moneda=res.moneda,
                version=res.version,
            ),
        )
    )


@router.get(
    "",
    response_model=InventoryPartListDocument,
    summary="Listar repuestos con paginación",
)
async def list_inventory_parts(
    empresa_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: ListInventoryPartsUseCase = Depends(get_list_inventory_parts_use_case),
) -> InventoryPartListDocument:
    """Retorna la colección paginada y controlada de repuestos de la empresa."""
    parts = await use_case.execute(empresa_id, limit=limit, offset=offset)
    return InventoryPartListDocument(
        data=[
            InventoryPartResource(
                id=p.id,
                attributes=InventoryPartAttributes(
                    empresa_id=p.empresa_id,
                    articulo_id=p.articulo_id,
                    proveedor_id=p.proveedor_id,
                    stock_actual=p.stock_actual,
                    stock_minimo=p.stock_minimo,
                    ubicacion_almacen=p.ubicacion_almacen,
                    precio_unitario=p.precio_unitario,
                    moneda=p.moneda,
                    version=p.version,
                ),
            )
            for p in parts
        ]
    )


@router.patch(
    "/{part_id}",
    response_model=InventoryPartDocument,
    summary="Actualizar parámetros del repuesto",
)
async def update_inventory_part(
    empresa_id: str,
    part_id: str,
    request: UpdateInventoryPartRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "edit")),
    use_case: UpdateInventoryPartUseCase = Depends(get_update_inventory_part_use_case),
) -> InventoryPartDocument:
    """Modifica de manera segura parámetros operativos y de precios bloqueando el stock_actual."""
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    
    dto = UpdateInventoryPartDTO(
        proveedor_id=sent.get("proveedor_id") if "proveedor_id" in sent else None,
        stock_minimo=sent.get("stock_minimo") if "stock_minimo" in sent else None,
        ubicacion_almacen=sent.get("ubicacion_almacen") if "ubicacion_almacen" in sent else None,
        precio_unitario=sent.get("precio_unitario") if "precio_unitario" in sent else None,
        moneda=sent.get("moneda") if "moneda" in sent else None,
        version=sent.get("version") if "version" in sent else None,
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(empresa_id, part_id, dto)
    return InventoryPartDocument(
        data=InventoryPartResource(
            id=res.id,
            attributes=InventoryPartAttributes(
                empresa_id=res.empresa_id,
                articulo_id=res.articulo_id,
                proveedor_id=res.proveedor_id,
                stock_actual=res.stock_actual,
                stock_minimo=res.stock_minimo,
                ubicacion_almacen=res.ubicacion_almacen,
                precio_unitario=res.precio_unitario,
                moneda=res.moneda,
                version=res.version,
            ),
        )
    )