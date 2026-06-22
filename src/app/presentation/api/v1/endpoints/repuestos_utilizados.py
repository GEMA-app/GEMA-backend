# src/app/presentation/api/v1/endpoints/repuestos_utilizados.py
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status

from app.application.dtos.repuesto_utilizado_dtos import (
    CreateRepuestoUtilizadoRequest as CreateRepuestoUtilizadoDTO,
)
from app.application.dtos.repuesto_utilizado_dtos import (
    UpdateRepuestoUtilizadoRequest as UpdateRepuestoUtilizadoDTO,
)
from app.composition.container import (
    create_repuesto_utilizado_use_case,
    delete_repuesto_utilizado_use_case,
    get_repuesto_utilizado_use_case,
    list_repuestos_utilizados_use_case,
    update_repuesto_utilizado_use_case,
)
from app.domain.enums import PermissionModule
from app.infrastructure.auth.dependencies import require_permission
from app.presentation.api.v1.schemas.repuestos_utilizados import (
    CreateRepuestoUtilizadoRequest,
    RepuestoUtilizadoDocument,
    RepuestosUtilizadosDocument,
    UpdateRepuestoUtilizadoRequest,
)
from app.presentation.api.v1.schemas.responses import NoContentResponse

router = APIRouter()


@router.get(
    "/",
    response_model=RepuestosUtilizadosDocument,
    status_code=status.HTTP_200_OK,
    summary="Lista repuestos utilizados",
    description="Obtiene todos los repuestos utilizados en una intervención específica.",
)
async def list_repuestos_utilizados(
    empresa_id: str = Path(..., description="ID de la empresa"),
    ot_id: str = Path(..., description="ID de la orden de trabajo"),
    intervencion_id: str = Path(..., description="ID de la intervención"),
    use_case=Depends(list_repuestos_utilizados_use_case),
    _=Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
):
    repuestos = await use_case.execute(empresa_id, intervencion_id)
    resources = [
        {
            "type": "repuesto-utilizado",
            "id": str(r.id),
            "attributes": {
                "empresa_id": str(r.empresa_id),
                "intervencion_id": str(r.intervencion_id),
                "repuesto_id": str(r.repuesto_id),
                "cantidad_usada": r.cantidad_usada,
                "precio_unitario": str(r.precio_unitario) if r.precio_unitario else None,
                "moneda": r.moneda,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            },
        }
        for r in repuestos
    ]
    return {"data": resources}


@router.post(
    "/",
    response_model=RepuestoUtilizadoDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Registra consumo de repuesto",
    description="Registra la salida de un repuesto consumido en una intervención.",
)
async def create_repuesto_utilizado(
    empresa_id: str = Path(..., description="ID de la empresa"),
    ot_id: str = Path(..., description="ID de la orden de trabajo"),
    intervencion_id: str = Path(..., description="ID de la intervención"),
    request: CreateRepuestoUtilizadoRequest,
    use_case=Depends(create_repuesto_utilizado_use_case),
    _=Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
):
    dto = CreateRepuestoUtilizadoDTO(
        intervencion_id=request.data.attributes.intervencion_id,
        repuesto_id=request.data.attributes.repuesto_id,
        cantidad_usada=request.data.attributes.cantidad_usada,
        precio_unitario=request.data.attributes.precio_unitario,
        moneda=request.data.attributes.moneda,
    )
    repuesto = await use_case.execute(empresa_id, dto)
    return {
        "data": {
            "type": "repuesto-utilizado",
            "id": str(repuesto.id),
            "attributes": {
                "empresa_id": str(repuesto.empresa_id),
                "intervencion_id": str(repuesto.intervencion_id),
                "repuesto_id": str(repuesto.repuesto_id),
                "cantidad_usada": repuesto.cantidad_usada,
                "precio_unitario": str(repuesto.precio_unitario) if repuesto.precio_unitario else None,
                "moneda": repuesto.moneda,
                "created_at": repuesto.created_at.isoformat() if repuesto.created_at else None,
                "updated_at": repuesto.updated_at.isoformat() if repuesto.updated_at else None,
            },
        }
    }


@router.get(
    "/{repuesto_id}",
    response_model=RepuestoUtilizadoDocument,
    status_code=status.HTTP_200_OK,
    summary="Obtiene detalle de consumo",
    description="Devuelve el detalle completo de un repuesto utilizado.",
)
async def get_repuesto_utilizado(
    empresa_id: str = Path(..., description="ID de la empresa"),
    ot_id: str = Path(..., description="ID de la orden de trabajo"),
    intervencion_id: str = Path(..., description="ID de la intervención"),
    repuesto_id: UUID = Path(..., description="ID del repuesto utilizado"),
    use_case=Depends(get_repuesto_utilizado_use_case),
    _=Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
):
    repuesto = await use_case.execute(repuesto_id)
    return {
        "data": {
            "type": "repuesto-utilizado",
            "id": str(repuesto.id),
            "attributes": {
                "empresa_id": str(repuesto.empresa_id),
                "intervencion_id": str(repuesto.intervencion_id),
                "repuesto_id": str(repuesto.repuesto_id),
                "cantidad_usada": repuesto.cantidad_usada,
                "precio_unitario": str(repuesto.precio_unitario) if repuesto.precio_unitario else None,
                "moneda": repuesto.moneda,
                "created_at": repuesto.created_at.isoformat() if repuesto.created_at else None,
                "updated_at": repuesto.updated_at.isoformat() if repuesto.updated_at else None,
            },
        }
    }


@router.patch(
    "/{repuesto_id}",
    response_model=RepuestoUtilizadoDocument,
    status_code=status.HTTP_200_OK,
    summary="Actualiza consumo de repuesto",
    description="Corrige la cantidad consumida y ajusta el movimiento de inventario.",
)
async def update_repuesto_utilizado(
    empresa_id: str = Path(..., description="ID de la empresa"),
    ot_id: str = Path(..., description="ID de la orden de trabajo"),
    intervencion_id: str = Path(..., description="ID de la intervención"),
    repuesto_id: UUID = Path(..., description="ID del repuesto utilizado"),
    request: UpdateRepuestoUtilizadoRequest,
    use_case=Depends(update_repuesto_utilizado_use_case),
    _=Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
):
    dto = UpdateRepuestoUtilizadoDTO(
        cantidad_usada=request.data.attributes.cantidad_usada,
    )
    repuesto = await use_case.execute(repuesto_id, dto)
    return {
        "data": {
            "type": "repuesto-utilizado",
            "id": str(repuesto.id),
            "attributes": {
                "empresa_id": str(repuesto.empresa_id),
                "intervencion_id": str(repuesto.intervencion_id),
                "repuesto_id": str(repuesto.repuesto_id),
                "cantidad_usada": repuesto.cantidad_usada,
                "precio_unitario": str(repuesto.precio_unitario) if repuesto.precio_unitario else None,
                "moneda": repuesto.moneda,
                "created_at": repuesto.created_at.isoformat() if repuesto.created_at else None,
                "updated_at": repuesto.updated_at.isoformat() if repuesto.updated_at else None,
            },
        }
    }


@router.delete(
    "/{repuesto_id}",
    response_model=NoContentResponse,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina consumo de repuesto",
    description="Revierte el consumo y restaura el stock del inventario.",
)
async def delete_repuesto_utilizado(
    empresa_id: str = Path(..., description="ID de la empresa"),
    ot_id: str = Path(..., description="ID de la orden de trabajo"),
    intervencion_id: str = Path(..., description="ID de la intervención"),
    repuesto_id: UUID = Path(..., description="ID del repuesto utilizado"),
    use_case=Depends(delete_repuesto_utilizado_use_case),
    _=Depends(require_permission(PermissionModule.MAINTENANCE, "delete")),
):
    await use_case.execute(repuesto_id)
    return None