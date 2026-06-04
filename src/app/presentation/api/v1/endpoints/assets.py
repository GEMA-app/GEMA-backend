from typing import Any, Optional
from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.asset_dtos import (
    CreateAssetRequest as CreateAssetDTO,
)
from app.application.dtos.asset_dtos import (
    UpdateAssetRequest as UpdateAssetDTO,
)
from app.application.use_cases.asset import (
    CreateAssetUseCase,
    DeleteAssetUseCase,
    GetAssetUseCase,
    ListAssetsUseCase,
    UpdateAssetUseCase,
)
from app.composition.container import (
    get_create_asset_use_case,
    get_delete_asset_use_case,
    get_get_asset_use_case,
    get_list_assets_use_case,
    get_update_asset_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.asset import (
    AssetAttributes,
    AssetDocument,
    AssetListDocument,
    AssetResource,
    CreateAssetRequest,
    UpdateAssetRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=AssetDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo activo",
)
async def create_asset(
    company_id: str,
    request: CreateAssetRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "create")),
    use_case: CreateAssetUseCase = Depends(get_create_asset_use_case),
) -> AssetDocument:
    dto = CreateAssetDTO(
        articulo_id=request.data.attributes.articulo_id,
        serial_interno=request.data.attributes.serial_interno,
        codigo_activo=request.data.attributes.codigo_activo,
        estado=request.data.attributes.estado,
        ubicacion_id=request.data.attributes.ubicacion_id,
        fecha_adquisicion=request.data.attributes.fecha_adquisicion,
        valor_monetario=request.data.attributes.valor_monetario,
        moneda=request.data.attributes.moneda,
    )
    res = await use_case.execute(company_id, dto)
    return AssetDocument(
        data=AssetResource(
            id=res.id,
            attributes=AssetAttributes(
                empresa_id=res.empresa_id,
                articulo_id=res.articulo_id,
                serial_interno=res.serial_interno,
                codigo_activo=res.codigo_activo,
                estado=res.estado,
                ubicacion_id=res.ubicacion_id,
                fecha_adquisicion=res.fecha_adquisicion,
                valor_monetario=res.valor_monetario,
                moneda=res.moneda,
            ),
        )
    )


@router.get(
    "",
    response_model=AssetListDocument,
    summary="Listar activos de la empresa con filtros",
)
async def list_assets(
    company_id: str,
    offset: int = 0,
    limit: int = 10,
    estado: Optional[str] = Query(None, description="Filtrar por estado del activo"),
    ubicacion_id: Optional[str] = Query(None, description="Filtrar por ID de ubicación"),
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "view")),
    use_case: ListAssetsUseCase = Depends(get_list_assets_use_case),
) -> AssetListDocument:
    filters = {}
    if estado is not None:
        filters["estado"] = estado
    if ubicacion_id is not None:
        filters["ubicacion_id"] = ubicacion_id

    assets, total = await use_case.execute(company_id, offset, limit, filters)
    return AssetListDocument(
        data=[
            AssetResource(
                id=a.id,
                attributes=AssetAttributes(
                    empresa_id=a.empresa_id,
                    articulo_id=a.articulo_id,
                    serial_interno=a.serial_interno,
                    codigo_activo=a.codigo_activo,
                    estado=a.estado,
                    ubicacion_id=a.ubicacion_id,
                    fecha_adquisicion=a.fecha_adquisicion,
                    valor_monetario=a.valor_monetario,
                    moneda=a.moneda,
                ),
            )
            for a in assets
        ],
        meta={"total": total},
    )


@router.get(
    "/{id}",
    response_model=AssetDocument,
    summary="Obtener activo por ID",
)
async def get_asset(
    company_id: str,
    id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "view")),
    use_case: GetAssetUseCase = Depends(get_get_asset_use_case),
) -> AssetDocument:
    res = await use_case.execute(company_id, id)
    return AssetDocument(
        data=AssetResource(
            id=res.id,
            attributes=AssetAttributes(
                empresa_id=res.empresa_id,
                articulo_id=res.articulo_id,
                serial_interno=res.serial_interno,
                codigo_activo=res.codigo_activo,
                estado=res.estado,
                ubicacion_id=res.ubicacion_id,
                fecha_adquisicion=res.fecha_adquisicion,
                valor_monetario=res.valor_monetario,
                moneda=res.moneda,
            ),
        )
    )


@router.patch(
    "/{id}",
    response_model=AssetDocument,
    summary="Actualizar activo",
)
async def update_asset(
    company_id: str,
    id: str,
    request: UpdateAssetRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "edit")),
    use_case: UpdateAssetUseCase = Depends(get_update_asset_use_case),
) -> AssetDocument:
    dto = UpdateAssetDTO(
        serial_interno=request.data.attributes.serial_interno,
        codigo_activo=request.data.attributes.codigo_activo,
        estado=request.data.attributes.estado,
        ubicacion_id=request.data.attributes.ubicacion_id,
        fecha_adquisicion=request.data.attributes.fecha_adquisicion,
        valor_monetario=request.data.attributes.valor_monetario,
        moneda=request.data.attributes.moneda,
    )
    res = await use_case.execute(company_id, id, dto)
    return AssetDocument(
        data=AssetResource(
            id=res.id,
            attributes=AssetAttributes(
                empresa_id=res.empresa_id,
                articulo_id=res.articulo_id,
                serial_interno=res.serial_interno,
                codigo_activo=res.codigo_activo,
                estado=res.estado,
                ubicacion_id=res.ubicacion_id,
                fecha_adquisicion=res.fecha_adquisicion,
                valor_monetario=res.valor_monetario,
                moneda=res.moneda,
            ),
        )
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar activo",
)
async def delete_asset(
    company_id: str,
    id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "delete")),
    use_case: DeleteAssetUseCase = Depends(get_delete_asset_use_case),
) -> None:
    await use_case.execute(company_id, id)
