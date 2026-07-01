"""Endpoints de consulta del historial de cambios de estado de activos (AssetStateLog)."""

from fastapi import APIRouter, Depends, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.use_cases.asset_state_log import ListAssetStateLogUseCase
from app.composition.container.asset_state_log import get_list_asset_state_log_use_case
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.asset_state_log import (
    AssetStateLogAttributes,
    AssetStateLogListDocument,
    AssetStateLogResource,
)

router = APIRouter()


@router.get(
    "/{activo_id}/historial-estados",
    response_model=AssetStateLogListDocument,
    status_code=status.HTTP_200_OK,
    summary="Trazabilidad de estados del activo",
)
async def list_asset_state_logs(
    empresa_id: str,
    activo_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ASSETS, "view")),
    use_case: ListAssetStateLogUseCase = Depends(get_list_asset_state_log_use_case),
) -> AssetStateLogListDocument:
    """Obtiene el historial de cambios de estado de un activo ordenado cronológicamente.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        activo_id: Identificador único del activo.
        current_user: Usuario autenticado con permiso de visualización.
        use_case: Caso de uso de listado de historial de estados.

    Returns:
        Documento JSON:API con la lista de cambios de estado del activo.
    """
    logs = await use_case.execute(empresa_id, activo_id)
    return AssetStateLogListDocument(
        data=[
            AssetStateLogResource(
                id=log.id,
                attributes=AssetStateLogAttributes(
                    empresa_id=log.empresa_id,
                    activo_id=log.activo_id,
                    estado_anterior=log.estado_anterior,
                    estado_nuevo=log.estado_nuevo,
                    motivo=log.motivo,
                    fecha_cambio=log.fecha_cambio,
                    usuario_id=log.usuario_id,
                    version=log.version,
                ),
            )
            for log in logs
        ],
    )
