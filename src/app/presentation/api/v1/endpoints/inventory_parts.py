"""Endpoints de la API REST para la gestión de repuestos de inventario (InventoryPart).

Cumple estrictamente con la especificación JSON:API de la plataforma GEMA.
"""

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.inventory_part_dtos import (
    CreateInventoryEntryRequest as CreateInventoryEntryDTO,
)
from app.application.dtos.inventory_part_dtos import (
    CreateInventoryPartRequest as CreateInventoryPartDTO,
)
from app.application.dtos.inventory_part_dtos import (
    UpdateInventoryPartRequest as UpdateInventoryPartDTO,
)
from app.application.use_cases.inventory_part.create_inventory_entry import (
    CreateInventoryEntryUseCase,
)
from app.application.use_cases.inventory_part.create_inventory_part import (
    CreateInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.delete_inventory_part import (
    DeleteInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.get_inventory_entry import GetInventoryEntryUseCase
from app.application.use_cases.inventory_part.get_inventory_part import GetInventoryPartUseCase
from app.application.use_cases.inventory_part.list_inventory_entries import (
    ListInventoryEntriesUseCase,
)
from app.application.use_cases.inventory_part.list_inventory_parts import ListInventoryPartsUseCase
from app.application.use_cases.inventory_part.update_inventory_part import (
    UpdateInventoryPartUseCase,
)
from app.composition.container.inventory_part import (
    get_create_inventory_entry_use_case,
    get_create_inventory_part_use_case,
    get_delete_inventory_part_use_case,
    get_get_inventory_entry_use_case,
    get_inventory_part_use_case,
    get_list_inventory_entries_use_case,
    get_list_inventory_parts_use_case,
    get_update_inventory_part_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
)
from app.presentation.api.v1.schemas.inventory_part import (
    CreateInventoryEntryRequest,
    CreateInventoryPartRequest,
    InventoryEntryAttributes,
    InventoryEntryDocument,
    InventoryEntryListDocument,
    InventoryEntryResource,
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
        stock_inicial=request.data.attributes.stock_actual,
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
    "/{repuesto_id}",
    response_model=InventoryPartDocument,
    summary="Obtener un repuesto por ID",
)
async def get_inventory_part(
    empresa_id: str,
    repuesto_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "view")),
    use_case: GetInventoryPartUseCase = Depends(get_inventory_part_use_case),
) -> InventoryPartDocument:
    """Obtiene los detalles informativos de un repuesto bajo aislamiento multi-tenant."""
    res = await use_case.execute(empresa_id, repuesto_id)
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
    bajo_minimo: bool = Query(False, description="Filtrar por stock bajo mínimo"),
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "view")),
    use_case: ListInventoryPartsUseCase = Depends(get_list_inventory_parts_use_case),
) -> InventoryPartListDocument:
    """Retorna la colección paginada y controlada de repuestos de la empresa."""
    parts, total = await use_case.execute(empresa_id, limit=limit, offset=offset, bajo_minimo=bajo_minimo)
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
        ],
        meta={"total": total},
    )


@router.patch(
    "/{repuesto_id}",
    response_model=InventoryPartDocument,
    summary="Actualizar parámetros del repuesto",
)
async def update_inventory_part(
    empresa_id: str,
    repuesto_id: str,
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
    res = await use_case.execute(empresa_id, repuesto_id, dto)
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


@router.post(
    "/{repuesto_id}/movimientos",
    response_model=InventoryEntryDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un movimiento (entrada o salida) de stock",
)
async def create_inventory_movement(
    empresa_id: str,
    repuesto_id: str,
    request: CreateInventoryEntryRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "create")),
    use_case: CreateInventoryEntryUseCase = Depends(get_create_inventory_entry_use_case),
) -> InventoryEntryDocument:
    """Registra una entrada o salida de inventario alterando de forma segura el stock actual.

    Garantiza la consistencia del inventario y guarda el log histórico del movimiento.
    """
    dto = CreateInventoryEntryDTO(
        repuesto_id=repuesto_id,
        movement_type=request.data.attributes.movement_type,
        quantity=request.data.attributes.quantity,
        work_order_id=request.data.attributes.work_order_id,
        usuario_id=current_user.id,
        reason=request.data.attributes.reason,
    )

    res = await use_case.execute(empresa_id, dto)

    return InventoryEntryDocument(
        data=InventoryEntryResource(
            id=res.id,
            attributes=InventoryEntryAttributes(
                empresa_id=res.empresa_id,
                repuesto_id=res.repuesto_id,
                movement_type=res.movement_type,
                quantity=res.quantity,
                work_order_id=res.work_order_id,
                usuario_id=res.usuario_id,
                precio_unitario=res.precio_unitario,
                moneda=res.moneda,
                fecha_movimiento=res.fecha_movimiento,
                reason=res.reason,
            ),
        )
    )


@router.get(
    "/{repuesto_id}/movimientos",
    response_model=InventoryEntryListDocument,
    summary="Listar movimientos de inventario de un repuesto",
)
async def list_inventory_movements(
    empresa_id: str,
    repuesto_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "view")),
    use_case: ListInventoryEntriesUseCase = Depends(get_list_inventory_entries_use_case),
) -> InventoryEntryListDocument:
    """Retorna el historial paginado de movimientos de un repuesto específico."""
    entries = await use_case.execute(empresa_id, repuesto_id, limit=limit, offset=offset)
    return InventoryEntryListDocument(
        data=[
            InventoryEntryResource(
                id=e.id,
                attributes=InventoryEntryAttributes(
                    empresa_id=e.empresa_id,
                    repuesto_id=e.repuesto_id,
                    movement_type=e.movement_type,
                    quantity=e.quantity,
                    work_order_id=e.work_order_id,
                    usuario_id=e.usuario_id,
                    precio_unitario=e.precio_unitario,
                    moneda=e.moneda,
                    fecha_movimiento=e.fecha_movimiento,
                    reason=e.reason,
                ),
            )
            for e in entries
        ]
    )


@router.get(
    "/{repuesto_id}/movimientos/{movimiento_id}",
    response_model=InventoryEntryDocument,
    summary="Obtener un movimiento de inventario por ID",
)
async def get_inventory_movement(
    empresa_id: str,
    repuesto_id: str,
    movimiento_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "view")),
    use_case: GetInventoryEntryUseCase = Depends(get_get_inventory_entry_use_case),
) -> InventoryEntryDocument:
    """Retorna los detalles de un movimiento de inventario específico."""
    res = await use_case.execute(empresa_id, movimiento_id)
    return InventoryEntryDocument(
        data=InventoryEntryResource(
            id=res.id,
            attributes=InventoryEntryAttributes(
                empresa_id=res.empresa_id,
                repuesto_id=res.repuesto_id,
                movement_type=res.movement_type,
                quantity=res.quantity,
                work_order_id=res.work_order_id,
                usuario_id=res.usuario_id,
                precio_unitario=res.precio_unitario,
                moneda=res.moneda,
                fecha_movimiento=res.fecha_movimiento,
                reason=res.reason,
            ),
        )
    )


@router.delete(
    "/{repuesto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un repuesto del inventario",
)
async def delete_inventory_part(
    empresa_id: str,
    repuesto_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.INVENTORY, "delete")),
    use_case: DeleteInventoryPartUseCase = Depends(get_delete_inventory_part_use_case),
) -> None:
    """Elimina un repuesto del inventario de la empresa."""
    await use_case.execute(empresa_id, repuesto_id)
