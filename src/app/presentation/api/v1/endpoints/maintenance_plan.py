"""Endpoints CRUD de planes de mantenimiento."""

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.maintenance_plan_dtos import (
    CreateMaintenancePlanRequest as CreateMaintenancePlanDTO,
)
from app.application.dtos.maintenance_plan_dtos import (
    UpdateMaintenancePlanRequest as UpdateMaintenancePlanDTO,
)
from app.application.use_cases.maintenance_plan import (
    CreateMaintenancePlanUseCase,
    DeleteMaintenancePlanUseCase,
    GetMaintenancePlanUseCase,
    ListMaintenancePlansUseCase,
    UpdateMaintenancePlanUseCase,
)
from app.composition.container import (
    get_create_maintenance_plan_use_case,
    get_delete_maintenance_plan_use_case,
    get_get_maintenance_plan_use_case,
    get_list_maintenance_plans_use_case,
    get_update_maintenance_plan_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.maintenance_plan import (
    CreateMaintenancePlanRequest,
    MaintenancePlanAttributes,
    MaintenancePlanDocument,
    MaintenancePlanListDocument,
    MaintenancePlanResource,
    UpdateMaintenancePlanRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=MaintenancePlanDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un plan de mantenimiento",
)
async def create_maintenance_plan(
    empresa_id: str,
    request: CreateMaintenancePlanRequest,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "create")
    ),
    use_case: CreateMaintenancePlanUseCase = Depends(get_create_maintenance_plan_use_case),
) -> MaintenancePlanDocument:
    """Crea un nuevo plan de mantenimiento para un activo.

    Args:
        empresa_id: Identificador de la empresa.
        request: Datos del plan en formato JSON:API.
        current_user: Usuario autenticado con permiso de creación.
        use_case: Caso de uso de creación.

    Returns:
        Documento JSON:API con los datos del plan creado.
    """
    dto = CreateMaintenancePlanDTO(
        activo_id=request.data.attributes.activo_id,
        nombre=request.data.attributes.nombre,
        tipo=request.data.attributes.tipo,
        intervalo_dias=request.data.attributes.intervalo_dias,
        proxima_ejecucion=request.data.attributes.proxima_ejecucion,
        tecnico_responsable_id=request.data.attributes.tecnico_responsable_id,
        descripcion_tareas=request.data.attributes.descripcion_tareas,
    )
    res = await use_case.execute(empresa_id, dto)
    return MaintenancePlanDocument(
        data=MaintenancePlanResource(
            id=res.id,
            attributes=MaintenancePlanAttributes(
                empresa_id=res.empresa_id,
                activo_id=res.activo_id,
                nombre=res.nombre,
                tipo=res.tipo,
                intervalo_dias=res.intervalo_dias,
                proxima_ejecucion=res.proxima_ejecucion,
                tecnico_responsable_id=res.tecnico_responsable_id,
                descripcion_tareas=res.descripcion_tareas,
                activo=res.activo,
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
        )
    )


@router.get(
    "",
    response_model=MaintenancePlanListDocument,
    summary="Listar planes de mantenimiento",
)
async def list_maintenance_plans(
    empresa_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    activo_id: str | None = Query(None, description="Filtrar por ID de activo"),
    tipo: str | None = Query(None, description="Filtrar por tipo de mantenimiento"),
    activo: bool | None = Query(None, description="Filtrar por estado activo/inactivo"),
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: ListMaintenancePlansUseCase = Depends(get_list_maintenance_plans_use_case),
) -> MaintenancePlanListDocument:
    """Lista los planes de mantenimiento de la empresa con filtros opcionales.

    Args:
        empresa_id: Identificador de la empresa.
        offset: Número de registros a omitir.
        limit: Máximo de registros a retornar.
        activo_id: Filtrar por activo asociado.
        tipo: Filtrar por tipo de mantenimiento.
        activo: Filtrar por estado activo/inactivo.
        current_user: Usuario autenticado con permiso de visualización.
        use_case: Caso de uso de listado.

    Returns:
        Documento JSON:API con la lista de planes y metadatos.
    """
    filters: dict[str, object] = {}
    if activo_id is not None:
        filters["activo_id"] = activo_id
    if tipo is not None:
        filters["tipo"] = tipo
    if activo is not None:
        filters["activo"] = activo

    plans, total = await use_case.execute(empresa_id, offset, limit, filters)
    return MaintenancePlanListDocument(
        data=[
            MaintenancePlanResource(
                id=p.id,
                attributes=MaintenancePlanAttributes(
                    empresa_id=p.empresa_id,
                    activo_id=p.activo_id,
                    nombre=p.nombre,
                    tipo=p.tipo,
                    intervalo_dias=p.intervalo_dias,
                    proxima_ejecucion=p.proxima_ejecucion,
                    tecnico_responsable_id=p.tecnico_responsable_id,
                    descripcion_tareas=p.descripcion_tareas,
                    activo=p.activo,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                ),
            )
            for p in plans
        ],
        meta={"total": total},
    )


@router.get(
    "/{plan_id}",
    response_model=MaintenancePlanDocument,
    summary="Obtener plan de mantenimiento por ID",
)
async def get_maintenance_plan(
    empresa_id: str,
    plan_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: GetMaintenancePlanUseCase = Depends(get_get_maintenance_plan_use_case),
) -> MaintenancePlanDocument:
    """Obtiene el detalle de un plan de mantenimiento.

    Args:
        empresa_id: Identificador de la empresa.
        plan_id: Identificador único del plan.
        current_user: Usuario autenticado con permiso de visualización.
        use_case: Caso de uso de obtención.

    Returns:
        Documento JSON:API con los datos del plan.
    """
    res = await use_case.execute(empresa_id, plan_id)
    return MaintenancePlanDocument(
        data=MaintenancePlanResource(
            id=res.id,
            attributes=MaintenancePlanAttributes(
                empresa_id=res.empresa_id,
                activo_id=res.activo_id,
                nombre=res.nombre,
                tipo=res.tipo,
                intervalo_dias=res.intervalo_dias,
                proxima_ejecucion=res.proxima_ejecucion,
                tecnico_responsable_id=res.tecnico_responsable_id,
                descripcion_tareas=res.descripcion_tareas,
                activo=res.activo,
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
        )
    )


@router.patch(
    "/{plan_id}",
    response_model=MaintenancePlanDocument,
    summary="Actualizar plan de mantenimiento",
)
async def update_maintenance_plan(
    empresa_id: str,
    plan_id: str,
    request: UpdateMaintenancePlanRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: UpdateMaintenancePlanUseCase = Depends(get_update_maintenance_plan_use_case),
) -> MaintenancePlanDocument:
    """Actualiza los datos de un plan de mantenimiento existente.

    Args:
        empresa_id: Identificador de la empresa.
        plan_id: Identificador único del plan.
        request: Datos actualizados en formato JSON:API.
        current_user: Usuario autenticado con permiso de edición.
        use_case: Caso de uso de actualización.

    Returns:
        Documento JSON:API con los datos actualizados del plan.
    """
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    dto = UpdateMaintenancePlanDTO(
        nombre=sent.get("nombre"),
        tipo=attrs.tipo if "tipo" in sent else None,
        intervalo_dias=sent.get("intervalo_dias"),
        proxima_ejecucion=sent.get("proxima_ejecucion"),
        tecnico_responsable_id=sent.get("tecnico_responsable_id"),
        descripcion_tareas=sent.get("descripcion_tareas"),
        activo=sent.get("activo"),
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(empresa_id, plan_id, dto)
    return MaintenancePlanDocument(
        data=MaintenancePlanResource(
            id=res.id,
            attributes=MaintenancePlanAttributes(
                empresa_id=res.empresa_id,
                activo_id=res.activo_id,
                nombre=res.nombre,
                tipo=res.tipo,
                intervalo_dias=res.intervalo_dias,
                proxima_ejecucion=res.proxima_ejecucion,
                tecnico_responsable_id=res.tecnico_responsable_id,
                descripcion_tareas=res.descripcion_tareas,
                activo=res.activo,
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
        )
    )


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar plan de mantenimiento",
)
async def delete_maintenance_plan(
    empresa_id: str,
    plan_id: str,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "delete")
    ),
    use_case: DeleteMaintenancePlanUseCase = Depends(get_delete_maintenance_plan_use_case),
) -> None:
    """Elimina un plan de mantenimiento.

    Args:
        empresa_id: Identificador de la empresa.
        plan_id: Identificador único del plan a eliminar.
        current_user: Usuario autenticado con permiso de eliminación.
        use_case: Caso de uso de eliminación.
    """
    await use_case.execute(empresa_id, plan_id)
