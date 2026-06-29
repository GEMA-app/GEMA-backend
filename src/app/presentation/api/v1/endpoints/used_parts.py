"""Endpoints REST para el módulo UsedPart (repuestos utilizados).

Rutas bajo: /v1/empresas/{empresa_id}/ordenes-trabajo/{ot_id}
/intervenciones/{intervencion_id}/repuestos-utilizados
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.used_part_dtos import (
    CreateUsedPartRequest as CreateUsedPartDTO,
)
from app.application.dtos.used_part_dtos import (
    UpdateUsedPartRequest as UpdateUsedPartDTO,
)
from app.application.use_cases.used_part.create_used_part import CreateUsedPartUseCase
from app.application.use_cases.used_part.delete_used_part import DeleteUsedPartUseCase
from app.application.use_cases.used_part.get_used_part import GetUsedPartUseCase
from app.application.use_cases.used_part.list_used_parts import ListUsedPartsUseCase
from app.application.use_cases.used_part.update_used_part import UpdateUsedPartUseCase
from app.composition.container.used_part import (
    get_create_used_part_use_case,
    get_delete_used_part_use_case,
    get_get_used_part_use_case,
    get_list_used_parts_use_case,
    get_update_used_part_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_dual_permission,
    require_permission,
)
from app.presentation.api.v1.schemas.used_parts import (
    CreateUsedPartRequest,
    UpdateUsedPartRequest,
    UsedPartAttributes,
    UsedPartDocument,
    UsedPartResource,
    UsedPartsDocument,
)

router = APIRouter()


@router.get(
    "",
    response_model=UsedPartsDocument,
    status_code=status.HTTP_200_OK,
    summary="Lista repuestos utilizados",
    description="Obtiene todos los repuestos utilizados en una intervención específica.",
)
async def list_used_parts(
    empresa_id: str,
    ot_id: str,
    intervencion_id: str,
    use_case: ListUsedPartsUseCase = Depends(get_list_used_parts_use_case),
    current_user: UserResponse = Depends(
        require_dual_permission(
            PermissionModule.MAINTENANCE, "view", PermissionModule.INVENTORY, "view"
        )
    ),
) -> UsedPartsDocument:
    """Lista los repuestos utilizados en una intervención.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        ot_id: Identificador de la orden de trabajo.
        intervencion_id: Identificador de la intervención técnica.
        use_case: Caso de uso inyectado.
        current_user: Usuario autenticado (validado por RBAC).

    Returns:
        UsedPartsDocument con la lista de repuestos utilizados.
    """
    parts = await use_case.execute(empresa_id, UUID(intervencion_id))
    return UsedPartsDocument(
        data=[
            UsedPartResource(
                id=str(p.id),
                attributes=UsedPartAttributes(
                    empresa_id=p.empresa_id,
                    intervencion_id=p.intervencion_id,
                    repuesto_id=p.repuesto_id,
                    cantidad_usada=p.cantidad_usada,
                    precio_unitario=p.precio_unitario,
                    moneda=p.moneda,
                    created_at=p.created_at.isoformat() if p.created_at else None,
                    updated_at=p.updated_at.isoformat() if p.updated_at else None,
                    precio_total=p.precio_total,
                ),
            )
            for p in parts
        ]
    )


@router.post(
    "",
    response_model=UsedPartDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Registra consumo de repuesto",
    description="Registra la salida de un repuesto consumido en una intervención.",
)
async def create_used_part(
    empresa_id: str,
    ot_id: str,
    intervencion_id: str,
    request: CreateUsedPartRequest,
    use_case: CreateUsedPartUseCase = Depends(get_create_used_part_use_case),
    current_user: UserResponse = Depends(
        require_dual_permission(
            PermissionModule.MAINTENANCE, "edit", PermissionModule.INVENTORY, "edit"
        )
    ),
) -> UsedPartDocument:
    """Crea un registro de repuesto utilizado.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        ot_id: Identificador de la orden de trabajo.
        intervencion_id: Identificador de la intervención técnica.
        request: Body JSON:API con los atributos del repuesto.
        use_case: Caso de uso inyectado.
        current_user: Usuario autenticado (validado por RBAC).

    Returns:
        UsedPartDocument con los datos del repuesto creado.
    """
    dto = CreateUsedPartDTO(
        intervencion_id=request.data.attributes.intervencion_id,
        repuesto_id=request.data.attributes.repuesto_id,
        cantidad_usada=request.data.attributes.cantidad_usada,
        precio_unitario=request.data.attributes.precio_unitario,
        moneda=request.data.attributes.moneda,
    )
    part = await use_case.execute(empresa_id, dto)
    return UsedPartDocument(
        data=UsedPartResource(
            id=str(part.id),
            attributes=UsedPartAttributes(
                empresa_id=part.empresa_id,
                intervencion_id=part.intervencion_id,
                repuesto_id=part.repuesto_id,
                cantidad_usada=part.cantidad_usada,
                precio_unitario=part.precio_unitario,
                moneda=part.moneda,
                created_at=part.created_at.isoformat() if part.created_at else None,
                updated_at=part.updated_at.isoformat() if part.updated_at else None,
                precio_total=part.precio_total,
            ),
        )
    )


@router.get(
    "/{used_part_id}",
    response_model=UsedPartDocument,
    status_code=status.HTTP_200_OK,
    summary="Obtiene detalle de consumo",
    description="Devuelve el detalle completo de un repuesto utilizado.",
)
async def get_used_part(
    empresa_id: str,
    ot_id: str,
    intervencion_id: str,
    used_part_id: UUID,
    use_case: GetUsedPartUseCase = Depends(get_get_used_part_use_case),
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
) -> UsedPartDocument:
    """Obtiene un repuesto utilizado por su ID.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        ot_id: Identificador de la orden de trabajo.
        intervencion_id: Identificador de la intervención técnica.
        used_part_id: UUID del registro de repuesto utilizado (PK de repuestos_utilizados).
        use_case: Caso de uso inyectado.
        current_user: Usuario autenticado (validado por RBAC).

    Returns:
        UsedPartDocument con los datos del repuesto.

    Raises:
        UsedPartNotFoundError: Si el repuesto no existe (404).
    """
    part = await use_case.execute(empresa_id, used_part_id)
    return UsedPartDocument(
        data=UsedPartResource(
            id=str(part.id),
            attributes=UsedPartAttributes(
                empresa_id=part.empresa_id,
                intervencion_id=part.intervencion_id,
                repuesto_id=part.repuesto_id,
                cantidad_usada=part.cantidad_usada,
                precio_unitario=part.precio_unitario,
                moneda=part.moneda,
                created_at=part.created_at.isoformat() if part.created_at else None,
                updated_at=part.updated_at.isoformat() if part.updated_at else None,
                precio_total=part.precio_total,
            ),
        )
    )


@router.patch(
    "/{used_part_id}",
    response_model=UsedPartDocument,
    status_code=status.HTTP_200_OK,
    summary="Actualiza consumo de repuesto",
    description="Corrige la cantidad consumida y ajusta el movimiento de inventario.",
)
async def update_used_part(
    empresa_id: str,
    ot_id: str,
    intervencion_id: str,
    used_part_id: UUID,
    request: UpdateUsedPartRequest,
    use_case: UpdateUsedPartUseCase = Depends(get_update_used_part_use_case),
    current_user: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
) -> UsedPartDocument:
    """Actualiza la cantidad de un repuesto utilizado.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        ot_id: Identificador de la orden de trabajo.
        intervencion_id: Identificador de la intervención técnica.
        used_part_id: UUID del registro de repuesto a actualizar (PK de repuestos_utilizados).
        request: Body JSON:API con los campos a actualizar.
        use_case: Caso de uso inyectado.
        current_user: Usuario autenticado (validado por RBAC).

    Returns:
        UsedPartDocument con los datos actualizados.

    Raises:
        UsedPartNotFoundError: Si el repuesto no existe (404).
    """
    dto = UpdateUsedPartDTO(
        cantidad_usada=request.data.attributes.cantidad_usada,
    )
    part = await use_case.execute(empresa_id, used_part_id, dto)
    return UsedPartDocument(
        data=UsedPartResource(
            id=str(part.id),
            attributes=UsedPartAttributes(
                empresa_id=part.empresa_id,
                intervencion_id=part.intervencion_id,
                repuesto_id=part.repuesto_id,
                cantidad_usada=part.cantidad_usada,
                precio_unitario=part.precio_unitario,
                moneda=part.moneda,
                created_at=part.created_at.isoformat() if part.created_at else None,
                updated_at=part.updated_at.isoformat() if part.updated_at else None,
                precio_total=part.precio_total,
            ),
        )
    )


@router.delete(
    "/{used_part_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina consumo de repuesto",
    description="Revierte el consumo y restaura el stock del inventario.",
)
async def delete_used_part(
    empresa_id: str,
    ot_id: str,
    intervencion_id: str,
    used_part_id: UUID,
    use_case: DeleteUsedPartUseCase = Depends(get_delete_used_part_use_case),
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "delete")
    ),
) -> None:
    """Elimina un repuesto utilizado.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        ot_id: Identificador de la orden de trabajo.
        intervencion_id: Identificador de la intervención técnica.
        used_part_id: UUID del registro de repuesto a eliminar (PK de repuestos_utilizados).
        use_case: Caso de uso inyectado.
        current_user: Usuario autenticado (validado por RBAC).

    Returns:
        None (HTTP 204 No Content).

    Raises:
        UsedPartNotFoundError: Si el repuesto no existe (404).
    """
    await use_case.execute(empresa_id, used_part_id)
    return None
