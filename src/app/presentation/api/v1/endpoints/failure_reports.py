"""Endpoints REST para el módulo de reportes de falla bajo JSON:API."""

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.failure_report_dtos import (
    CreateFailureReportRequest as CreateFailureReportDTO,
)
from app.application.dtos.failure_report_dtos import (
    UpdateFailureReportRequest as UpdateFailureReportDTO,
)
from app.application.use_cases.failure_report import (
    CreateFailureReportUseCase,
    DeleteFailureReportUseCase,
    GetFailureReportUseCase,
    ListFailureReportsUseCase,
    UpdateFailureReportUseCase,
)
from app.composition.container import (
    get_create_failure_report_use_case,
    get_delete_failure_report_use_case,
    get_failure_report_use_case,
    get_list_failure_reports_use_case,
    get_update_failure_report_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.failure_report import (
    CreateFailureReportRequest,
    FailureReportAttributes,
    FailureReportDocument,
    FailureReportListDocument,
    FailureReportResource,
    UpdateFailureReportRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=FailureReportDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un reporte de falla",
)
async def create_failure_report(
    empresa_id: str,
    request: CreateFailureReportRequest,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "create")
    ),
    use_case: CreateFailureReportUseCase = Depends(get_create_failure_report_use_case),
) -> FailureReportDocument:
    """Crea un nuevo reporte de falla dentro de una empresa.

    Args:
        empresa_id: Identificador UUID de la empresa.
        request: Cuerpo de la solicitud con los atributos del reporte.
        current_user: Usuario autenticado con permiso de creación.
        use_case: Caso de uso inyectado para la creación.

    Returns:
        Documento JSON:API con el reporte de falla creado.
    """
    attrs = request.data.attributes
    dto = CreateFailureReportDTO(
        empresa_id=empresa_id,
        title=attrs.title,
        description=attrs.description,
        location=attrs.location,
        priority=attrs.priority,
        reported_by=attrs.reported_by,
        activo_id=attrs.activo_id,
    )
    res = await use_case.execute(empresa_id, dto)
    return FailureReportDocument(
        data=FailureReportResource(
            id=res.id,
            attributes=FailureReportAttributes(
                title=res.title,
                description=res.description,
                location=res.location,
                priority=res.priority,
                reported_by=res.reported_by,
                status=res.status,
                created_at=res.created_at,
                activo_id=res.activo_id,
                version=res.version,
                orden_trabajo_id=res.orden_trabajo_id,
            ),
        )
    )


@router.get(
    "",
    response_model=FailureReportListDocument,
    summary="Listar reportes de falla con filtros",
)
async def list_failure_reports(
    empresa_id: str,
    offset: int = 0,
    limit: int = 10,
    status: str | None = Query(None, description="Filtrar por estado"),
    priority: str | None = Query(None, description="Filtrar por prioridad"),
    search: str | None = Query(
        None, min_length=2, max_length=100, description="Buscar por título o descripción"
    ),
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: ListFailureReportsUseCase = Depends(get_list_failure_reports_use_case),
) -> FailureReportListDocument:
    """Lista los reportes de falla de una empresa con paginación y filtros opcionales.

    Args:
        empresa_id: Identificador UUID de la empresa.
        offset: Número de registros a omitir (paginación).
        limit: Máximo de registros a retornar.
        status: Filtro opcional por estado del reporte.
        priority: Filtro opcional por prioridad.
        search: Término de búsqueda en título o descripción.
        current_user: Usuario autenticado con permiso de lectura.
        use_case: Caso de uso inyectado para listar.

    Returns:
        Documento JSON:API con la colección de reportes y metadatos de paginación.
    """
    filters = {}
    if status is not None:
        filters["status"] = status
    if priority is not None:
        filters["priority"] = priority
    if search is not None:
        filters["search"] = search

    reports, total = await use_case.execute(empresa_id, offset, limit, filters)
    return FailureReportListDocument(
        data=[
            FailureReportResource(
                id=r.id,
                attributes=FailureReportAttributes(
                    title=r.title,
                    description=r.description,
                    location=r.location,
                    priority=r.priority,
                    reported_by=r.reported_by,
                    status=r.status,
                    created_at=r.created_at,
                    activo_id=r.activo_id,
                    version=r.version,
                    orden_trabajo_id=r.orden_trabajo_id,
                ),
            )
            for r in reports
        ],
        meta={"total": total},
    )


@router.get(
    "/{reporte_id}",
    response_model=FailureReportDocument,
    summary="Obtener reporte de falla por ID",
)
async def get_failure_report(
    empresa_id: str,
    reporte_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
    use_case: GetFailureReportUseCase = Depends(get_failure_report_use_case),
) -> FailureReportDocument:
    """Obtiene un reporte de falla por su ID dentro de una empresa.

    Args:
        empresa_id: Identificador UUID de la empresa.
        reporte_id: Identificador UUID del reporte de falla.
        current_user: Usuario autenticado con permiso de lectura.
        use_case: Caso de uso inyectado para obtener.

    Returns:
        Documento JSON:API con el reporte de falla solicitado.

    Raises:
        FailureReportNotFoundError: Si el reporte no existe en la empresa.
    """
    res = await use_case.execute(empresa_id, reporte_id)
    return FailureReportDocument(
        data=FailureReportResource(
            id=res.id,
            attributes=FailureReportAttributes(
                title=res.title,
                description=res.description,
                location=res.location,
                priority=res.priority,
                reported_by=res.reported_by,
                status=res.status,
                created_at=res.created_at,
                activo_id=res.activo_id,
                version=res.version,
                orden_trabajo_id=res.orden_trabajo_id,
            ),
        )
    )


@router.patch(
    "/{reporte_id}",
    response_model=FailureReportDocument,
    summary="Actualizar reporte de falla",
)
async def update_failure_report(
    empresa_id: str,
    reporte_id: str,
    request: UpdateFailureReportRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
    use_case: UpdateFailureReportUseCase = Depends(get_update_failure_report_use_case),
) -> FailureReportDocument:
    """Actualiza parcialmente un reporte de falla existente.

    Args:
        empresa_id: Identificador UUID de la empresa.
        reporte_id: Identificador UUID del reporte a actualizar.
        request: Cuerpo de la solicitud con los atributos a modificar.
        current_user: Usuario autenticado con permiso de edición.
        use_case: Caso de uso inyectado para la actualización.

    Returns:
        Documento JSON:API con el reporte de falla actualizado.

    Raises:
        FailureReportNotFoundError: Si el reporte no existe en la empresa.
    """
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    dto = UpdateFailureReportDTO(
        title=sent.get("title"),
        description=sent.get("description"),
        location=sent.get("location"),
        priority=sent.get("priority"),
        reported_by=sent.get("reported_by"),
        status=sent.get("status"),
        activo_id=sent.get("activo_id"),
        version=sent.get("version"),
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(empresa_id, reporte_id, dto)
    return FailureReportDocument(
        data=FailureReportResource(
            id=res.id,
            attributes=FailureReportAttributes(
                title=res.title,
                description=res.description,
                location=res.location,
                priority=res.priority,
                reported_by=res.reported_by,
                status=res.status,
                created_at=res.created_at,
                activo_id=res.activo_id,
                version=res.version,
                orden_trabajo_id=res.orden_trabajo_id,
            ),
        )
    )


@router.delete(
    "/{reporte_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reporte de falla",
)
async def delete_failure_report(
    empresa_id: str,
    reporte_id: str,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "delete")
    ),
    use_case: DeleteFailureReportUseCase = Depends(get_delete_failure_report_use_case),
) -> None:
    """Elimina un reporte de falla por su ID dentro de una empresa.

    Args:
        empresa_id: Identificador UUID de la empresa.
        reporte_id: Identificador UUID del reporte a eliminar.
        current_user: Usuario autenticado con permiso de eliminación.
        use_case: Caso de uso inyectado para la eliminación.

    Raises:
        FailureReportNotFoundError: Si el reporte no existe en la empresa.
    """
    await use_case.execute(empresa_id, reporte_id)
