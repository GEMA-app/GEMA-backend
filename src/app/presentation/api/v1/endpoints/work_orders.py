"""Endpoints REST para el módulo de órdenes de trabajo (JSON:API).

Proporciona las rutas CRUD y de cambio de estado para órdenes de
trabajo, con paginación, filtros y permisos RBAC.
"""

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
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
    AssignTechnicianUseCase,
    ChangeWorkOrderStatusUseCase,
    CreateWorkOrderUseCase,
    DeleteWorkOrderUseCase,
    GetWorkOrderStatusHistoryUseCase,
    GetWorkOrderUseCase,
    ListWorkOrdersUseCase,
    RemoveTechnicianUseCase,
    UpdateWorkOrderUseCase,
    ValidateWorkOrderUseCase,
)
from app.composition.container import (
    get_assign_technician_use_case,
    get_change_work_order_status_use_case,
    get_create_work_order_use_case,
    get_delete_work_order_use_case,
    get_get_work_order_status_history_use_case,
    get_list_work_orders_use_case,
    get_remove_technician_use_case,
    get_update_work_order_use_case,
    get_validate_work_order_use_case,
    get_work_order_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.work_order import (
    AssignTechnicianRequest,
    ChangeStatusRequest,
    CreateWorkOrderRequest,
    UpdateWorkOrderRequest,
    WorkOrderAttributes,
    WorkOrderDocument,
    WorkOrderListDocument,
    WorkOrderResource,
    WorkOrderStatusLogAttributes,
    WorkOrderStatusLogListDocument,
    WorkOrderStatusLogResource,
)

router = APIRouter()


@router.post(
    "",
    response_model=WorkOrderDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una orden de trabajo",
)
async def create_work_order(
    empresa_id: str,
    request: CreateWorkOrderRequest,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "create")
    ),
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
    res = await use_case.execute(empresa_id, dto)
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
                version=res.version,
            ),
        )
    )


@router.get(
    "",
    response_model=WorkOrderListDocument,
    summary="Listar órdenes de trabajo",
)
async def list_work_orders(
    empresa_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: ListWorkOrdersUseCase = Depends(get_list_work_orders_use_case),
    estado: str | None = Query(None, description="Filtrar por estado"),
    activo_id: str | None = Query(None, description="Filtrar por activo"),
    tipo: str | None = Query(None, description="Filtrar por tipo de mantenimiento"),
    supervisor_id: str | None = Query(None, description="Filtrar por supervisor"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
) -> WorkOrderListDocument:
    """Lista órdenes de trabajo de una empresa con paginación y filtros."""
    results, total = await use_case.execute(
        empresa_id,
        estado=estado,
        activo_id=activo_id,
        tipo=tipo,
        supervisor_id=supervisor_id,
        offset=offset,
        limit=limit,
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
                    version=r.version,
                ),
            )
            for r in results
        ],
        meta={"total": total, "offset": offset, "limit": limit},
    )


@router.get(
    "/{ot_id}",
    response_model=WorkOrderDocument,
    summary="Obtener una orden de trabajo",
)
async def get_work_order(
    empresa_id: str,
    ot_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: GetWorkOrderUseCase = Depends(get_work_order_use_case),
) -> WorkOrderDocument:
    """Obtiene los detalles de una orden de trabajo por su ID."""
    res = await use_case.execute(empresa_id, ot_id)
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
                version=res.version,
            ),
        )
    )


@router.patch(
    "/{ot_id}",
    response_model=WorkOrderDocument,
    summary="Actualizar una orden de trabajo",
)
async def update_work_order(
    empresa_id: str,
    ot_id: str,
    request: UpdateWorkOrderRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: UpdateWorkOrderUseCase = Depends(get_update_work_order_use_case),
) -> WorkOrderDocument:
    """Actualiza los detalles de una orden de trabajo existente."""
    dto = UpdateWorkOrderDTO(
        descripcion_trabajo=request.data.attributes.descripcion_trabajo,
        costo_estimado=request.data.attributes.costo_estimado,
        costo_real=request.data.attributes.costo_real,
        supervisor_id=request.data.attributes.supervisor_id,
    )
    res = await use_case.execute(empresa_id, ot_id, dto)
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
                version=res.version,
            ),
        )
    )


@router.delete(
    "/{ot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una orden de trabajo",
)
async def delete_work_order(
    empresa_id: str,
    ot_id: str,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "delete")
    ),
    use_case: DeleteWorkOrderUseCase = Depends(get_delete_work_order_use_case),
) -> None:
    """Elimina una orden de trabajo por su ID."""
    await use_case.execute(empresa_id, ot_id)


@router.patch(
    "/{ot_id}/estado",
    response_model=WorkOrderDocument,
    summary="Cambiar estado de una orden de trabajo",
)
async def change_work_order_status(
    empresa_id: str,
    ot_id: str,
    request: ChangeStatusRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: ChangeWorkOrderStatusUseCase = Depends(get_change_work_order_status_use_case),
) -> WorkOrderDocument:
    """Cambia el estado de una orden de trabajo (iniciar, pausar, reanudar, cerrar, cancelar)."""
    dto = ChangeStatusDTO(estado=request.data.attributes.estado)
    res = await use_case.execute(empresa_id, ot_id, dto)
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
                version=res.version,
            ),
        )
    )


@router.post(
    "/{ot_id}/asignar-tecnico",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Asignar técnico a orden de trabajo",
)
async def assign_technician(
    empresa_id: str,
    ot_id: str,
    request: AssignTechnicianRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: AssignTechnicianUseCase = Depends(get_assign_technician_use_case),
) -> None:
    """Asigna un técnico a una orden de trabajo."""
    await use_case.execute(empresa_id, ot_id, request.data.attributes.tecnico_id)


@router.delete(
    "/{ot_id}/remover-tecnico",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover técnico de orden de trabajo",
)
async def remove_technician(
    empresa_id: str,
    ot_id: str,
    tecnico_id: str = Query(..., description="ID del técnico a remover"),
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: RemoveTechnicianUseCase = Depends(get_remove_technician_use_case),
) -> None:
    """Remueve un técnico de una orden de trabajo."""
    await use_case.execute(empresa_id, ot_id, tecnico_id)


@router.post(
    "/{ot_id}/validar",
    response_model=WorkOrderDocument,
    summary="Validar una orden de trabajo",
)
async def validate_work_order(
    empresa_id: str,
    ot_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: ValidateWorkOrderUseCase = Depends(get_validate_work_order_use_case),
) -> WorkOrderDocument:
    """Valida una orden de trabajo cerrándola de forma definitiva por un supervisor."""
    res = await use_case.execute(empresa_id, ot_id, current_user.id)
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
                version=res.version,
            ),
        )
    )


@router.get(
    "/{ot_id}/historial-estados",
    response_model=WorkOrderStatusLogListDocument,
    summary="Obtener historial de estados de orden de trabajo",
)
async def get_work_order_status_history(
    empresa_id: str,
    ot_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: GetWorkOrderStatusHistoryUseCase = Depends(
        get_get_work_order_status_history_use_case
    ),
) -> WorkOrderStatusLogListDocument:
    """Retorna la lista de transiciones de estado que ha tenido una orden de trabajo."""
    logs = await use_case.execute(empresa_id, ot_id)
    return WorkOrderStatusLogListDocument(
        data=[
            WorkOrderStatusLogResource(
                id=log.id,
                attributes=WorkOrderStatusLogAttributes(
                    ordenes_trabajo_id=log.ordenes_trabajo_id,
                    estado_anterior=log.estado_anterior,
                    estado_nuevo=log.estado_nuevo,
                    usuario_id=log.usuario_id,
                    motivo=log.motivo,
                    fecha_cambio=log.fecha_cambio,
                ),
            )
            for log in logs
        ]
    )
