from datetime import datetime
from typing import Any, List, Optional  # Añadido 'Any' aquí
from fastapi import APIRouter, Depends, Query, status

# 1. Schemas de respuesta
from app.presentation.api.v1.schemas.system_audit import SystemAuditResponse

# 2. Permisos y Dependencias del sistema
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission

# 3. Casos de uso y Contenedor
from app.application.use_cases.system_audit import (
    ListSystemAuditsUseCase,
    GetSystemAuditUseCase,
)
from app.composition.container import (
    get_list_system_audits_use_case,
    get_system_audit_use_case,
)

router = APIRouter()


@router.get(
    "",
    response_model=List[SystemAuditResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar auditorías del sistema con filtros",
)
async def list_system_audits(
    empresa_id: str,
    offset: int = 0,
    limit: int = 10,
    usuario_id: Optional[int] = Query(None, description="Filtrar por el ID del usuario"),
    accion: Optional[str] = Query(None, description="Filtrar por la acción ejecutada"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial del rango"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final del rango"),
    current_user: Any = Depends(require_permission(PermissionModule.SYSTEM_AUDIT, "view")), 
    use_case: ListSystemAuditsUseCase = Depends(get_list_system_audits_use_case),
) -> List[SystemAuditResponse]:
    """
    Lista las auditorías de sistema de la empresa con soporte de filtros y rangos de fecha.
    """
    filters = {}
    if usuario_id is not None:
        filters["usuario_id"] = usuario_id
    if accion:
        filters["accion"] = accion
    if fecha_inicio:
        filters["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        filters["fecha_fin"] = fecha_fin

    # Ejecutamos el caso de uso delegado
    auditorias = await use_case.execute(empresa_id, offset, limit, filters)
    return auditorias


@router.get(
    "/{auditoria_id}",
    response_model=SystemAuditResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener una auditoría por ID",
)
async def get_system_audit(
    empresa_id: str,
    auditoria_id: int,
    current_user: Any = Depends(require_permission(PermissionModule.SYSTEM_AUDIT, "view")),
    use_case: GetSystemAuditUseCase = Depends(get_system_audit_use_case),
) -> SystemAuditResponse:
    """
    Obtiene los detalles completos de un registro de auditoría específico.
    """
    auditoria = await use_case.execute(empresa_id, auditoria_id)
    return auditoria