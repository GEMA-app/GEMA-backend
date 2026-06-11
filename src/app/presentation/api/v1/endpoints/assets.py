from typing import Any
from uuid import UUID

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
    get_list_assets_use_case,
    get_update_asset_use_case,
    provide_asset_use_case,
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
        estado=request.data.attributes.estado.value,
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
                version=res.version,
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
    estado: str | None = Query(None, description="Filtrar por estado del activo"),
    ubicacion_id: UUID | None = Query(None, description="Filtrar por ID de ubicación"),
    search: str | None = Query(None, min_length=2, max_length=100, description="Buscar por codigo o serial"),
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "view")),
    use_case: ListAssetsUseCase = Depends(get_list_assets_use_case),
) -> AssetListDocument:
    filters = {}
    if estado is not None:
        filters["estado"] = estado
    if ubicacion_id is not None:
        filters["ubicacion_id"] = str(ubicacion_id)
    if search is not None:
        filters["search"] = search

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
                    version=a.version,
                ),
            )
            for a in assets
        ],
        meta={"total": total},
    )


@router.get(
    "/{asset_id}",
    response_model=AssetDocument,
    summary="Obtener activo por ID",
)
async def get_asset(
    company_id: str,
    asset_id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "view")),
    use_case: GetAssetUseCase = Depends(provide_asset_use_case),
) -> AssetDocument:
    res = await use_case.execute(company_id, asset_id)
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
                version=res.version,
            ),
        )
    )


@router.patch(
    "/{asset_id}",
    response_model=AssetDocument,
    summary="Actualizar activo",
)
async def update_asset(
    company_id: str,
    asset_id: str,
    request: UpdateAssetRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "edit")),
    use_case: UpdateAssetUseCase = Depends(get_update_asset_use_case),
) -> AssetDocument:
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    dto = UpdateAssetDTO(
        serial_interno=sent.get("serial_interno") if "serial_interno" in sent else None,
        codigo_activo=sent.get("codigo_activo") if "codigo_activo" in sent else None,
        estado=attrs.estado.value if ("estado" in sent and attrs.estado) else None,
        ubicacion_id=sent.get("ubicacion_id") if "ubicacion_id" in sent else None,
        fecha_adquisicion=sent.get("fecha_adquisicion") if "fecha_adquisicion" in sent else None,
        valor_monetario=sent.get("valor_monetario") if "valor_monetario" in sent else None,
        moneda=sent.get("moneda") if "moneda" in sent else None,
        version=sent.get("version") if "version" in sent else None,
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(company_id, asset_id, dto)
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
                version=res.version,
            ),
        )
    )


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar activo",
)
async def delete_asset(
    company_id: str,
    asset_id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ASSETS, "delete")),
    use_case: DeleteAssetUseCase = Depends(get_delete_asset_use_case),
) -> None:
    await use_case.execute(company_id, asset_id)
