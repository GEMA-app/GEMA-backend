"""Endpoints for the technical interventions module."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.intervention_dtos import (
    CreateInterventionRequest,
    UpdateInterventionRequest,
)
from app.application.use_cases.intervention import (
    CreateInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
)
from app.composition.container.intervention import (
    get_create_intervention_use_case,
    get_intervention_use_case,
    get_list_interventions_use_case,
    get_update_intervention_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import require_permission
from app.presentation.api.v1.schemas.interventions import (
    InterventionDocument,
    InterventionListDocument,
    InterventionResource,
)
from app.presentation.api.v1.schemas.interventions import (
    UpdateInterventionRequest as UpdateInterventionSchema,
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
                attributes=i,
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
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
) -> InterventionDocument:
    """Create a new technical intervention.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID (passed separately from the body).
        request: DTO with the intervention data.
        use_case: Injected use case for creating interventions.
        _: Authorization dependency (MAINTENANCE:edit permission).

    Returns:
        InterventionDocument with the created intervention.
    """
    intervention = await use_case.execute(ot_id, request)

    return InterventionDocument(
        data=InterventionResource(
            id=str(intervention.id),
            type="intervenciones",
            attributes=intervention,
        )
    )


@router.get(
    "/{intervention_id}",
    response_model=InterventionDocument,
    status_code=status.HTTP_200_OK,
    summary="Get intervention",
    description="Gets the details of a technical intervention by its ID.",
)
async def get_intervention(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    ot_id: Annotated[str, Path(description="ID de la orden de trabajo")],
    intervention_id: Annotated[str, Path(description="ID de la intervenciÃ³n")],
    use_case: GetInterventionUseCase = Depends(get_intervention_use_case),
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "view")),
) -> InterventionDocument:
    """Get a technical intervention by its ID.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID.
        intervention_id: Intervention UUID.
        use_case: Injected use case for getting interventions.
        _: Authorization dependency (MAINTENANCE:view permission).

    Returns:
        InterventionDocument with the intervention details.
    """
    intervention = await use_case.execute(ot_id, intervention_id, empresa_id)

    return InterventionDocument(
        data=InterventionResource(
            id=str(intervention.id),
            type="intervenciones",
            attributes=intervention,
        )
    )


@router.patch(
    "/{intervention_id}",
    response_model=InterventionDocument,
    status_code=status.HTTP_200_OK,
    summary="Update intervention",
    description="Updates an existing technical intervention.",
)
async def update_intervention(
    empresa_id: Annotated[str, Path(description="ID de la empresa")],
    ot_id: Annotated[str, Path(description="ID de la orden de trabajo")],
    intervention_id: Annotated[str, Path(description="ID de la intervenciÃ³n")],
    request: UpdateInterventionSchema,
    use_case: UpdateInterventionUseCase = Depends(get_update_intervention_use_case),
    _: UserResponse = Depends(require_permission(PermissionModule.MAINTENANCE, "edit")),
) -> InterventionDocument:
    """Update an existing technical intervention.

    Args:
        empresa_id: Company UUID.
        ot_id: Work order UUID.
        intervention_id: Intervention UUID.
        request: JSON:API schema with attributes to update.
        use_case: Injected use case for updating interventions.
        _: Authorization dependency (MAINTENANCE:edit permission).

    Returns:
        InterventionDocument with the updated intervention.
    """
    dto_request = UpdateInterventionRequest(
        tareas_realizadas=request.data.attributes.tareas_realizadas,
        horas_hombre=request.data.attributes.horas_hombre,
    )
    intervention = await use_case.execute(ot_id, intervention_id, empresa_id, dto_request)

    return InterventionDocument(
        data=InterventionResource(
            id=str(intervention.id),
            type="intervenciones",
            attributes=intervention,
        )
    )

