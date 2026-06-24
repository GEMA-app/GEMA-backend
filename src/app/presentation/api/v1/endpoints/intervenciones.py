"""Endpoints para el módulo de intervenciones técnicas."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.application.dtos.intervencion_dtos import (
    ActualizarIntervencionRequest,
    CrearIntervencionRequest,
    IntervencionResponse,
)
from app.application.use_cases.intervencion import (
    ActualizarIntervencionUseCase,
    CrearIntervencionUseCase,
    ListarIntervencionesUseCase,
    ObtenerIntervencionUseCase,
)
from app.composition.container.intervencion import (
    get_actualizar_intervencion_use_case,
    get_crear_intervencion_use_case,
    get_listar_intervenciones_use_case,
    get_obtener_intervencion_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.dependencies import require_permission
from app.presentation.api.v1.schemas.intervenciones import (
    IntervencionDocument,
    IntervencionListDocument,
    IntervencionResource,
    UpdateIntervencionRequest,
)

router = APIRouter(prefix="/empresas/{empresa_id}/intervenciones", tags=["intervenciones"])


@router.get(
    "",
    response_model=IntervencionListDocument,
    status_code=status.HTTP_200_OK,
    summary="Listar intervenciones",
    description="Obtiene una lista paginada de intervenciones técnicas de la empresa.",
)
async def listar_intervenciones(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    offset: Annotated[int, Query(ge=0, description="Número de registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad de registros a obtener")] = 20,
    use_case: ListarIntervencionesUseCase = Depends(get_listar_intervenciones_use_case),
    _: None = Depends(require_permission(PermissionModule.WORK_ORDERS, "view")),
) -> IntervencionListDocument:
    """Endpoint para listar intervenciones de una empresa."""
    intervenciones, total = await use_case.execute(empresa_id, offset, limit)

    return IntervencionListDocument(
        data=[
            IntervencionResource(
                id=str(i.id),
                type="intervenciones",
                attributes=i,
            )
            for i in intervenciones
        ],
        meta={"total": total, "offset": offset, "limit": limit},
    )


@router.post(
    "",
    response_model=IntervencionDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear intervención",
    description="Crea una nueva intervención técnica en una orden de trabajo.",
)
async def crear_intervencion(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    request: CrearIntervencionRequest,
    use_case: CrearIntervencionUseCase = Depends(get_crear_intervencion_use_case),
    _: None = Depends(require_permission(PermissionModule.WORK_ORDERS, "edit")),
) -> IntervencionDocument:
    """Endpoint para crear una nueva intervención."""
    intervencion = await use_case.execute(request)

    return IntervencionDocument(
        data=IntervencionResource(
            id=str(intervencion.id),
            type="intervenciones",
            attributes=intervencion,
        )
    )


@router.get(
    "/{intervencion_id}",
    response_model=IntervencionDocument,
    status_code=status.HTTP_200_OK,
    summary="Obtener intervención",
    description="Obtiene los detalles de una intervención técnica por su ID.",
)
async def obtener_intervencion(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    intervencion_id: Annotated[str, Path(description="ID de la intervención")],
    use_case: ObtenerIntervencionUseCase = Depends(get_obtener_intervencion_use_case),
    _: None = Depends(require_permission(PermissionModule.WORK_ORDERS, "view")),
) -> IntervencionDocument:
    """Endpoint para obtener una intervención específica."""
    intervencion = await use_case.execute(intervencion_id, empresa_id)

    return IntervencionDocument(
        data=IntervencionResource(
            id=str(intervencion.id),
            type="intervenciones",
            attributes=intervencion,
        )
    )


@router.patch(
    "/{intervencion_id}",
    response_model=IntervencionDocument,
    status_code=status.HTTP_200_OK,
    summary="Actualizar intervención",
    description="Actualiza los datos de una intervención técnica existente.",
)
async def actualizar_intervencion(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    intervencion_id: Annotated[str, Path(description="ID de la intervención")],
    request: UpdateIntervencionRequest,
    use_case: ActualizarIntervencionUseCase = Depends(get_actualizar_intervencion_use_case),
    _: None = Depends(require_permission(PermissionModule.WORK_ORDERS, "edit")),
) -> IntervencionDocument:
    """Endpoint para actualizar una intervención existente."""
    # Convertir el schema de entrada al DTO de aplicación
    dto_request = ActualizarIntervencionRequest(
        descripcion=request.data.attributes.descripcion,
        horas_trabajadas=request.data.attributes.horas_trabajadas,
        costo=request.data.attributes.costo,
        observaciones=request.data.attributes.observaciones,
    )
    intervencion = await use_case.execute(intervencion_id, empresa_id, dto_request)

    return IntervencionDocument(
        data=IntervencionResource(
            id=str(intervencion.id),
            type="intervenciones",
            attributes=intervencion,
        )
    )