from fastapi import APIRouter, Depends, Query, Path, status
from app.application.dtos.system_audit_dtos import ListSystemAuditsRequest
from app.application.use_cases.system_audit import GetSystemAuditUseCase, ListSystemAuditsUseCase
from app.composition.container import get_get_system_audit_use_case, get_list_system_audits_use_case
from app.presentation.api.v1.schemas.system_audit import (
    SystemAuditDocument,
    SystemAuditListDocument,
    SystemAuditResource,
    SystemAuditAttributes,
    SystemAuditMeta,
)

router = APIRouter(prefix="/system-audits", tags=["Auditorías de Sistema"])


@router.get("", response_model=SystemAuditListDocument, status_code=status.HTTP_200_OK)
async def list_system_audits(
    empresa_id: str = Query(..., description="ID de la empresa/tenant", alias="empresa_id"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    accion: Optional[str] = Query(None, description="Filtrar por acción ejecutada"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros por página"),
    use_case: ListSystemAuditsUseCase = Depends(get_list_system_audits_use_case),
):
    """
    Endpoint para listar y filtrar el historial de auditorías bajo el formato JSON:API.
    """
    # 1. Agrupamos los filtros en el DTO de entrada esperado por la aplicación
    request_dto = ListSystemAuditsRequest(usuario_id=usuario_id, accion=accion)
    
    # 2. Ejecutamos la lógica de negocio a través del caso de uso
    dtos, total = await use_case.execute(
        company_id_str=empresa_id, offset=offset, limit=limit, request=request_dto
    )
    
    # 3. Traducimos los DTOs planos al estándar estricto JSON:API de presentación
    resources = [
        SystemAuditResource(
            id=str(dto.id),
            attributes=SystemAuditAttributes(
                usuario_id=dto.usuario_id,
                accion=dto.accion,
                detalles=dto.detalles,
                ip_address=dto.ip_address,
                ocurrido_en=dto.ocurrido_en,
            ),
        )
        for dto in dtos
    ]
    
    return SystemAuditListDocument(
        data=resources, 
        meta=SystemAuditMeta(total=total, offset=offset, limit=limit)
    )


@router.get("/{id}", response_model=SystemAuditDocument, status_code=status.HTTP_200_OK)
async def get_system_audit_by_id(
    empresa_id: str = Query(..., description="ID de la empresa/tenant"),
    id: int = Path(..., description="ID de la auditoría"),
    use_case: GetSystemAuditUseCase = Depends(get_get_system_audit_use_case),
):
    """
    Endpoint para obtener el detalle profundo de una auditoría por su ID único.
    """
    dto = await use_case.execute(company_id_str=empresa_id, auditoria_id=id)
    
    return SystemAuditDocument(
        data=SystemAuditResource(
            id=str(dto.id),
            attributes=SystemAuditAttributes(
                usuario_id=dto.usuario_id,
                accion=dto.accion,
                detalles=dto.detalles,
                ip_address=dto.ip_address,
                ocurrido_en=dto.ocurrido_en,
            ),
        )
    )