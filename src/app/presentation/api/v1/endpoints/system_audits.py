from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.system_audit_dtos import ListSystemAuditsRequest
from app.application.use_cases.system_audit import GetSystemAuditUseCase, ListSystemAuditsUseCase
from app.composition.container import get_list_system_audits_use_case, get_system_audit_use_case
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.system_audit import (
    SystemAuditAttributes,
    SystemAuditDocument,
    SystemAuditListDocument,
    SystemAuditMeta,
    SystemAuditResource,
)

router = APIRouter(tags=["Auditorías de Sistema"])


@router.get("", response_model=SystemAuditListDocument, status_code=status.HTTP_200_OK)
async def list_system_audits(
    empresa_id: str,
    usuario_id: str | None = Query(None, description="Filtrar por ID de usuario"),
    accion: str | None = Query(None, description="Filtrar por acción ejecutada"),
    modulo: str | None = Query(None, description="Filtrar por módulo"),
    fecha_inicio: datetime | None = Query(None, description="Filtrar desde fecha"),
    fecha_fin: datetime | None = Query(None, description="Filtrar hasta fecha"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros por página"),
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "view")),
    use_case: ListSystemAuditsUseCase = Depends(get_list_system_audits_use_case),
) -> SystemAuditListDocument:
    """Lista y filtra el historial de auditorías en formato JSON:API.

    Args:
        empresa_id: UUID de la empresa/tenant.
        usuario_id: Filtro opcional por ID de usuario.
        accion: Filtro opcional por acción ejecutada.
        modulo: Filtro opcional por módulo.
        fecha_inicio: Filtro opcional desde fecha.
        fecha_fin: Filtro opcional hasta fecha.
        offset: Número de registros a saltar.
        limit: Límite de registros por página.
        current_user: Usuario autenticado validado con permiso.
        use_case: Caso de uso inyectado.

    Returns:
        SystemAuditListDocument con recursos, meta y paginación.
    """
    request_dto = ListSystemAuditsRequest(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    dtos, total = await use_case.execute(
        company_id_str=empresa_id,
        offset=offset,
        limit=limit,
        request=request_dto,
    )
    resources = [
        SystemAuditResource(
            id=str(dto.id),
            attributes=SystemAuditAttributes(
                usuario_id=dto.usuario_id,
                accion=dto.accion,
                detalles=dto.detalles,
                ip_address=dto.ip_address,
                ocurrido_en=dto.ocurrido_en,
                usuario_nombre=dto.usuario_nombre,
                usuario_email=dto.usuario_email,
                modulo=dto.modulo,
                descripcion=dto.descripcion,
            ),
        )
        for dto in dtos
    ]
    return SystemAuditListDocument(
        data=resources,
        meta=SystemAuditMeta(total=total, offset=offset, limit=limit),
    )


@router.get(
    "/{auditoria_id}",
    response_model=SystemAuditDocument,
    status_code=status.HTTP_200_OK,
)
async def get_system_audit_by_id(
    empresa_id: str,
    auditoria_id: UUID = Path(..., description="ID de la auditoría"),
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "view")),
    use_case: GetSystemAuditUseCase = Depends(get_system_audit_use_case),
) -> SystemAuditDocument:
    """Obtiene el detalle de una auditoría por su ID único.

    Args:
        empresa_id: UUID de la empresa/tenant.
        auditoria_id: ID numérico de la auditoría.
        current_user: Usuario autenticado validado con permiso.
        use_case: Caso de uso inyectado.

    Returns:
        SystemAuditDocument con el recurso de auditoría.
    """
    dto = await use_case.execute(company_id_str=empresa_id, audit_id=auditoria_id)
    return SystemAuditDocument(
        data=SystemAuditResource(
            id=str(dto.id),
            attributes=SystemAuditAttributes(
                usuario_id=dto.usuario_id,
                accion=dto.accion,
                detalles=dto.detalles,
                ip_address=dto.ip_address,
                ocurrido_en=dto.ocurrido_en,
                usuario_nombre=dto.usuario_nombre,
                usuario_email=dto.usuario_email,
                modulo=dto.modulo,
                descripcion=dto.descripcion,
            ),
        )
    )
