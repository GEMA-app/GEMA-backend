"""Endpoints REST para el módulo de órdenes de trabajo (JSON:API).

Proporciona las rutas CRUD y de cambio de estado para órdenes de
trabajo, con paginación, filtros y permisos RBAC.
"""

from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.work_order_dtos import (
    ChangeWorkOrderStatusRequest as ChangeStatusDTO,
)
from app.application.dtos.work_order_dtos import (
    CreateWorkOrderRequest as CreateWorkOrderDTO,
)
from app.application.dtos.work_order_dtos import (
    UpdateWorkOrderRequest as UpdateWorkOrderDTO,
)
from app.application.use_cases.work_order import (
    ChangeWorkOrderStatusUseCase,
    CreateWorkOrderUseCase,
    DeleteWorkOrderUseCase,
    GetWorkOrderUseCase,
    ListWorkOrdersUseCase,
    UpdateWorkOrderUseCase,
)
from app.composition.container import (
    get_change_work_order_status_use_case,
    get_create_work_order_use_case,
    get_delete_work_order_use_case,
    get_list_work_orders_use_case,
    get_update_work_order_use_case,
    get_work_order_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.work_orders import (
    ChangeStatusRequest,
    CreateWorkOrderRequest,
    UpdateWorkOrderRequest,
    WorkOrderAttributes,
    WorkOrderDocument,
    WorkOrderListDocument,
    WorkOrderResource,
)

router = APIRouter()


@router.post(
    "",
    response_model=WorkOrderDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una orden de trabajo",
)
async def create_work_order(
    company_id: str,
    request: CreateWorkOrderRequest,
    current_user: Any = Depends(require_permission(PermissionModule.MAINTENANCE, "create")),
    use_case: CreateWorkOrderUseCase = Depends(get_create_work_order_use_case),
) -> WorkOrderDocument:
    """Crea una nueva orden de trabajo."""
    dto = CreateWorkOrderDTO(
        activo_id=request.data.attributes.activo_id,
        tipo=request.data.attributes.tipo,
        codigo_ot=request.data.attributes.codigo_ot,
        supervisor_id=request.data.attributes.supervisor_id,
        descripcion_trabajo=request.data.attributes.descripcion_trabajo,
        costo_estimado=request.data.attributes.costo_estimado,
        moneda=request.data.attributes.moneda,
    )
    res = await use_case.execute(company_id, dto)
    return WorkOrderDocument(
        data=WorkOrderResource(
            id=res.id,
            attributes=WorkOrderAttributes(
                company_id=res.company_id,
                codigo_ot=res.codigo_ot,
                activo_id=res.activo_id,
                reporte_id=res.reporte_id,
                tipo=res.tipo,
                estado=res.estado,
                supervisor_id=res.supervisor_id,
                fecha_apertura=res.fecha_apertura,
                fecha_inicio_trabajo=res.fecha_inicio_trabajo,
                fecha_cierre=res.fecha_cierre,
                descripcion_trabajo=res.descripcion_trabajo,
                costo_estimado=res.costo_estimado,
                costo_real=res.costo_real,
                moneda=res.moneda,
                validado_por_id=res.validado_por_id,
                fecha_validacion=res.fecha_validacion,
            ),
        )
    )


@router.get(
    "",
    response_model=WorkOrderListDocument,
    summary="Listar órdenes de trabajo",
)
async def list_work_orders(
    company_id: str,
    current_user: Any = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: ListWorkOrdersUseCase = Depends(get_list_work_orders_use_case),
    estado: str | None = Query(None, description="Filtrar por estado"),
    activo_id: str | None = Query(None, description="Filtrar por activo"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
) -> WorkOrderListDocument:
    """Lista órdenes de trabajo de una empresa con paginación y filtros."""
    results, total = await use_case.execute(
        company_id, estado=estado, activo_id=activo_id
    )
    return WorkOrderListDocument(
        data=[
            WorkOrderResource(
                id=r.id,
                attributes=WorkOrderAttributes(
                    company_id=r.company_id,
                    codigo_ot=r.codigo_ot,
                    activo_id=r.activo_id,
                    reporte_id=r.reporte_id,
                    tipo=r.tipo,
                    estado=r.estado,
                    supervisor_id=r.supervisor_id,
                    fecha_apertura=r.fecha_apertura,
                    fecha_inicio_trabajo=r.fecha_inicio_trabajo,
                    fecha_cierre=r.fecha_cierre,
                    descripcion_trabajo=r.descripcion_trabajo,
                    costo_estimado=r.costo_estimado,
                    costo_real=r.costo_real,
                    moneda=r.moneda,
                    validado_por_id=r.validado_por_id,
                    fecha_validacion=r.fecha_validacion,
                ),
            )
            for r in results[offset : offset + limit]
        ],
        meta={"total": total, "offset": offset, "limit": limit},
    )


@router.get(
    "/{work_order_id}",
    response_model=WorkOrderDocument,
    summary="Obtener una orden de trabajo",
)
async def get_work_order(
    company_id: str,
    work_order_id: str,
    current_user: Any = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: GetWorkOrderUseCase = Depends(get_work_order_use_case),
) -> WorkOrderDocument:
    """Obtiene los detalles de una orden de trabajo por su ID."""
    res = await use_case.execute(company_id, work_order_id)
    return WorkOrderDocument(
        data=WorkOrderResource(
            id=res.id,
            attributes=WorkOrderAttributes(
                company_id=res.company_id,
                codigo_ot=res.codigo_ot,
                activo_id=res.activo_id,
                reporte_id=res.reporte_id,
                tipo=res.tipo,
                estado=res.estado,
                supervisor_id=res.supervisor_id,
                fecha_apertura=res.fecha_apertura,
                fecha_inicio_trabajo=res.fecha_inicio_trabajo,
                fecha_cierre=res.fecha_cierre,
                descripcion_trabajo=res.descripcion_trabajo,
                costo_estimado=res.costo_estimado,
                costo_real=res.costo_real,
                moneda=res.moneda,
                validado_por_id=res.validado_por_id,
                fecha_validacion=res.fecha_validacion,
            ),
        )
    )


@router.patch(
    "/{work_order_id}",
    response_model=WorkOrderDocument,
    summary="Actualizar una orden de trabajo",
)
async def update_work_order(
    company_id: str,
    work_order_id: str,
    request: UpdateWorkOrderRequest,
    current_user: Any = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: UpdateWorkOrderUseCase = Depends(get_update_work_order_use_case),
) -> WorkOrderDocument:
    """Actualiza los detalles de una orden de trabajo existente."""
    dto = UpdateWorkOrderDTO(
        descripcion_trabajo=request.data.attributes.descripcion_trabajo,
        costo_estimado=request.data.attributes.costo_estimado,
        costo_real=request.data.attributes.costo_real,
        supervisor_id=request.data.attributes.supervisor_id,
    )
    res = await use_case.execute(company_id, work_order_id, dto)
    return WorkOrderDocument(
        data=WorkOrderResource(
            id=res.id,
            attributes=WorkOrderAttributes(
                company_id=res.company_id,
                codigo_ot=res.codigo_ot,
                activo_id=res.activo_id,
                reporte_id=res.reporte_id,
                tipo=res.tipo,
                estado=res.estado,
                supervisor_id=res.supervisor_id,
                fecha_apertura=res.fecha_apertura,
                fecha_inicio_trabajo=res.fecha_inicio_trabajo,
                fecha_cierre=res.fecha_cierre,
                descripcion_trabajo=res.descripcion_trabajo,
                costo_estimado=res.costo_estimado,
                costo_real=res.costo_real,
                moneda=res.moneda,
                validado_por_id=res.validado_por_id,
                fecha_validacion=res.fecha_validacion,
            ),
        )
    )


@router.delete(
    "/{work_order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una orden de trabajo",
)
async def delete_work_order(
    company_id: str,
    work_order_id: str,
    current_user: Any = Depends(require_permission(PermissionModule.MAINTENANCE, "delete")),
    use_case: DeleteWorkOrderUseCase = Depends(get_delete_work_order_use_case),
) -> None:
    """Elimina una orden de trabajo por su ID."""
    await use_case.execute(company_id, work_order_id)


@router.patch(
    "/{work_order_id}/estado",
    response_model=WorkOrderDocument,
    summary="Cambiar estado de una orden de trabajo",
)
async def change_work_order_status(
    company_id: str,
    work_order_id: str,
    request: ChangeStatusRequest,
    current_user: Any = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: ChangeWorkOrderStatusUseCase = Depends(
        get_change_work_order_status_use_case
    ),
) -> WorkOrderDocument:
    """Cambia el estado de una orden de trabajo (iniciar, pausar, reanudar, cerrar, cancelar)."""
    dto = ChangeStatusDTO(estado=request.data.attributes.estado)
    res = await use_case.execute(company_id, work_order_id, dto)
    return WorkOrderDocument(
        data=WorkOrderResource(
            id=res.id,
            attributes=WorkOrderAttributes(
                company_id=res.company_id,
                codigo_ot=res.codigo_ot,
                activo_id=res.activo_id,
                reporte_id=res.reporte_id,
                tipo=res.tipo,
                estado=res.estado,
                supervisor_id=res.supervisor_id,
                fecha_apertura=res.fecha_apertura,
                fecha_inicio_trabajo=res.fecha_inicio_trabajo,
                fecha_cierre=res.fecha_cierre,
                descripcion_trabajo=res.descripcion_trabajo,
                costo_estimado=res.costo_estimado,
                costo_real=res.costo_real,
                moneda=res.moneda,
                validado_por_id=res.validado_por_id,
                fecha_validacion=res.fecha_validacion,
            ),
        )
    )
