"""Endpoints REST para ejecuciones de plan de mantenimiento.

Prefix: /v1/empresas/{empresa_id}/planes-mantenimiento/{plan_id}/ejecuciones
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.plan_execution_dtos import (
    PlanExecutionCreateRequest as PlanExecutionCreateDTO,
)
from app.application.dtos.plan_execution_dtos import (
    PlanExecutionResponse,
)
from app.application.use_cases.plan_execution import (
    CreatePlanExecutionUseCase,
    GetPlanExecutionUseCase,
    ListPlanExecutionUseCase,
)
from app.composition.container.plan_execution import (
    create_plan_execution_use_case,
    get_plan_execution_use_case,
    list_plan_execution_use_case,
)
from app.domain.enums import PermissionModule
from app.domain.exceptions.plan_execution import (
    PlanExecutionNotFoundError,
)
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
    require_tenant_read,
)
from app.presentation.api.v1.schemas.plan_execution import (
    CreatePlanExecutionRequest as CreatePlanExecutionSchema,
)
from app.presentation.api.v1.schemas.plan_execution import (
    PlanExecutionAttributes,
    PlanExecutionDocument,
    PlanExecutionListDocument,
    PlanExecutionResource,
)

router = APIRouter()


@router.get("")
async def list_plan_executions(
    empresa_id: str,
    plan_id: str,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "view")
    ),
    use_case: ListPlanExecutionUseCase = Depends(list_plan_execution_use_case),
) -> PlanExecutionListDocument:
    """Lista todas las ejecuciones de un plan de mantenimiento.

    Args:
        empresa_id: ID de la empresa.
        plan_id: ID del plan de mantenimiento.
        current_user: Usuario autenticado validado por tenant.
        use_case: Caso de uso de listado.

    Returns:
        Documento JSON:API con la lista de ejecuciones.
    """
    result = await use_case.execute(empresa_id, plan_id)
    resources = [_to_resource(item) for item in result.data]
    return PlanExecutionListDocument(data=resources)


@router.post("", status_code=201)
async def create_plan_execution(
    empresa_id: str,
    plan_id: str,
    body: CreatePlanExecutionSchema,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "create")
    ),
    use_case: CreatePlanExecutionUseCase = Depends(create_plan_execution_use_case),
) -> PlanExecutionDocument:
    """Crea una nueva ejecución de plan de mantenimiento.

    Args:
        empresa_id: ID de la empresa.
        plan_id: ID del plan de mantenimiento.
        body: Cuerpo de la solicitud JSON:API.
        current_user: Usuario autenticado con permiso.
        use_case: Caso de uso de creación.

    Returns:
        Documento JSON:API con la ejecución creada.
    """
    attrs = body.data.attributes
    dto = PlanExecutionCreateDTO(
        plan_id=UUID(plan_id),
        work_order_id=UUID(attrs.work_order_id) if attrs.work_order_id else None,
        execution_date=attrs.execution_date,
        observations=attrs.observations,
    )
    result = await use_case.execute(empresa_id, dto)
    return PlanExecutionDocument(data=_to_resource(result))


@router.get("/{ejecucion_id}")
async def get_plan_execution(
    empresa_id: str,
    ejecucion_id: str,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.MAINTENANCE, "view")
    ),
    use_case: GetPlanExecutionUseCase = Depends(get_plan_execution_use_case),
) -> PlanExecutionDocument:
    """Obtiene una ejecución de plan por su ID.

    Args:
        empresa_id: ID de la empresa.
        ejecucion_id: ID de la ejecución.
        current_user: Usuario autenticado validado por tenant.
        use_case: Caso de uso de obtención.

    Returns:
        Documento JSON:API con la ejecución solicitada.

    Raises:
        PlanExecutionNotFoundError: Si no existe la ejecución.
    """
    # ponytail: validación UUID mínima, el use case lanza 404 si no existe.
    try:
        UUID(ejecucion_id)
    except ValueError:
        raise PlanExecutionNotFoundError(ejecucion_id, empresa_id) from None

    result = await use_case.execute(empresa_id, ejecucion_id)
    return PlanExecutionDocument(data=_to_resource(result))


def _to_resource(dto: PlanExecutionResponse) -> PlanExecutionResource:
    """Convierte un DTO de respuesta a un recurso JSON:API.

    Args:
        dto: DTO de respuesta de ejecución de plan.

    Returns:
        Recurso JSON:API de ejecución de plan.
    """
    attributes = PlanExecutionAttributes(
        empresa_id=dto.empresa_id,
        plan_id=dto.plan_id,
        work_order_id=dto.work_order_id,
        execution_date=dto.execution_date,
        observations=dto.observations,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )
    return PlanExecutionResource(
        id=dto.id,
        type="planExecution",
        attributes=attributes,
    )
