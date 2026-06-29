"""Endpoints for the technical interventions module."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.intervention_dtos import (
    CreateInterventionRequest as CreateInterventionDTO,
)
from app.application.dtos.intervention_dtos import (
    UpdateInterventionRequest as UpdateInterventionDTO,
)
from app.application.use_cases.intervention import (
    CreateInterventionUseCase,
    DeleteInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
)
from app.composition.container.intervention import (
    get_create_intervention_use_case,
    get_delete_intervention_use_case,
    get_intervention_use_case,
    get_list_interventions_use_case,
    get_update_intervention_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.interventions import (
    CreateInterventionRequest,
    InterventionAttributes,
    InterventionDocument,
    InterventionListDocument,
    InterventionResource,
    UpdateInterventionRequest,
)

router = APIRouter(
    prefix="/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones",
    tags=["intervenciones"],
)


@router.get(
    "",
    response_model=InterventionListDocument,
    status_code=status.HTTP_200_OK,
    summary="List interventions",
    description="Gets a paginated list of technical interventions for a work order.",
)
async def list_interventions(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    ot_id: Annotated[str, Path(description="ID de la orden de trabajo")],
    offset: Annotated[int, Query(ge=0, description="NÃºmero de registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad de registros a obtener")] = 20,
    use_case: ListInterventionsUseCase = Depends(get_list_interventions_use_case),
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
) -> InterventionListDocument:
    """List technical interventions for a work order.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID.
        offset: Number of records to skip (pagination).
        limit: Maximum number of records to return.
        use_case: Injected use case for listing interventions.
        _: Authorization dependency (MAINTENANCE:view permission).

    Returns:
        InterventionListDocument with paginated interventions.
    """
    interventions, total = await use_case.execute(ot_id, empresa_id, offset, limit)

    return InterventionListDocument(
        data=[
            InterventionResource(
                id=str(i.id),
                type="intervenciones",
                attributes=InterventionAttributes(
                    work_order_id=i.work_order_id,
                    technician_id=i.technician_id,
                    tareas_realizadas=i.tareas_realizadas,
                    fecha_inicio=i.fecha_inicio,
                    fecha_fin=i.fecha_fin,
                    horas_hombre=i.horas_hombre,
                ),
            )
            for i in interventions
        ],
        meta={"total": total, "offset": offset, "limit": limit},
    )


@router.post(
    "",
    response_model=InterventionDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Create intervention",
    description="Creates a new technical intervention in a work order.",
)
async def create_intervention(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    ot_id: Annotated[str, Path(description="ID de la orden de trabajo")],
    request: CreateInterventionRequest,
    use_case: CreateInterventionUseCase = Depends(get_create_intervention_use_case),
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "create")),
) -> InterventionDocument:
    """Create a new technical intervention.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID (passed separately from the body).
        request: Schema with the intervention data.
        use_case: Injected use case for creating interventions.
        _: Authorization dependency (MAINTENANCE:create permission).

    Returns:
        InterventionDocument with the created intervention.
    """
    attrs = request.data.attributes
    dto = CreateInterventionDTO(
        technician_id=attrs.technician_id,
        tareas_realizadas=attrs.tareas_realizadas,
        fecha_inicio=attrs.fecha_inicio,
        horas_hombre=attrs.horas_hombre,
    )
    intervention = await use_case.execute(empresa_id, ot_id, dto)

    return InterventionDocument(
        data=InterventionResource(
            id=str(intervention.id),
            type="intervenciones",
            attributes=InterventionAttributes(
                work_order_id=intervention.work_order_id,
                technician_id=intervention.technician_id,
                tareas_realizadas=intervention.tareas_realizadas,
                fecha_inicio=intervention.fecha_inicio,
                fecha_fin=intervention.fecha_fin,
                horas_hombre=intervention.horas_hombre,
            ),
        )
    )


@router.get(
    "/{intervencion_id}",
    response_model=InterventionDocument,
    status_code=status.HTTP_200_OK,
    summary="Get intervention",
    description="Gets the details of a technical intervention by its ID.",
)
async def get_intervention(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    ot_id: Annotated[str, Path(description="ID de la orden de trabajo")],
    intervencion_id: Annotated[str, Path(description="ID de la intervención")],
    use_case: GetInterventionUseCase = Depends(get_intervention_use_case),
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
) -> InterventionDocument:
    """Get a technical intervention by its ID.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID.
        intervencion_id: Intervention UUID.
        use_case: Injected use case for getting interventions.
        _: Authorization dependency (MAINTENANCE:view permission).

    Returns:
        InterventionDocument with the intervention details.
    """
    intervention = await use_case.execute(ot_id, intervencion_id, empresa_id)

    return InterventionDocument(
        data=InterventionResource(
            id=str(intervention.id),
            type="intervenciones",
            attributes=InterventionAttributes(
                work_order_id=intervention.work_order_id,
                technician_id=intervention.technician_id,
                tareas_realizadas=intervention.tareas_realizadas,
                fecha_inicio=intervention.fecha_inicio,
                fecha_fin=intervention.fecha_fin,
                horas_hombre=intervention.horas_hombre,
            ),
        )
    )


@router.patch(
    "/{intervencion_id}",
    response_model=InterventionDocument,
    status_code=status.HTTP_200_OK,
    summary="Update intervention",
    description="Updates an existing technical intervention.",
)
async def update_intervention(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    ot_id: Annotated[str, Path(description="ID de la orden de trabajo")],
    intervencion_id: Annotated[str, Path(description="ID de la intervención")],
    request: UpdateInterventionRequest,
    use_case: UpdateInterventionUseCase = Depends(get_update_intervention_use_case),
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
) -> InterventionDocument:
    """Update an existing technical intervention.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID.
        intervencion_id: Intervention UUID.
        request: JSON:API schema with attributes to update.
        use_case: Injected use case for updating interventions.
        _: Authorization dependency (MAINTENANCE:edit permission).

    Returns:
        InterventionDocument with the updated intervention.
    """
    attrs = request.data.attributes
    dto_request = UpdateInterventionDTO(
        tareas_realizadas=attrs.tareas_realizadas,
        horas_hombre=attrs.horas_hombre,
    )
    intervention = await use_case.execute(ot_id, intervencion_id, empresa_id, dto_request)

    return InterventionDocument(
        data=InterventionResource(
            id=str(intervention.id),
            type="intervenciones",
            attributes=InterventionAttributes(
                work_order_id=intervention.work_order_id,
                technician_id=intervention.technician_id,
                tareas_realizadas=intervention.tareas_realizadas,
                fecha_inicio=intervention.fecha_inicio,
                fecha_fin=intervention.fecha_fin,
                horas_hombre=intervention.horas_hombre,
            ),
        )
    )


@router.delete(
    "/{intervencion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete intervention",
    description="Deletes a technical intervention by its ID.",
)
async def delete_intervention(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    ot_id: Annotated[str, Path(description="ID de la orden de trabajo")],
    intervencion_id: Annotated[str, Path(description="ID de la intervención")],
    use_case: DeleteInterventionUseCase = Depends(get_delete_intervention_use_case),
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "delete")),
) -> None:
    """Delete a technical intervention.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID.
        intervencion_id: Intervention UUID.
        use_case: Injected use case for deleting interventions.
        _: Authorization dependency (MAINTENANCE:delete permission).
    """
    await use_case.execute(ot_id, intervencion_id, empresa_id)

