"""Endpoints CRUD de planes de suscripción: creación, listado, obtención,
actualización y eliminación de planes de suscripción."""


from fastapi import APIRouter, Depends, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.subscription_plan_dtos import (
    CreateSubscriptionPlanRequest as CreateSubscriptionPlanDTO,
    UpdateSubscriptionPlanRequest as UpdateSubscriptionPlanDTO,
)
from app.application.use_cases.subscription_plan import (
    CreateSubscriptionPlanUseCase,
    DeleteSubscriptionPlanUseCase,
    GetSubscriptionPlanUseCase,
    UpdateSubscriptionPlanUseCase,
    ListSubscriptionPlansUseCase
)
from app.composition.container import (
    get_create_subscription_plan_use_case,
    get_delete_subscription_plan_use_case,
    get_subscription_plan_use_case,
    get_update_subscription_plan_use_case,
    get_list_subscription_plans_use_case
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import get_current_active_user, require_permission
from app.presentation.api.v1.schemas.subscription_plan import (
    SubscriptionPlanAttributes,
    SubscriptionPlanResource,
    SubscriptionPlanDocument,
    SubscriptionPlanListDocument,
    UpdateSubscriptionPlanRequest,
    CreateSubscriptionPlanRequest
)

router = APIRouter()

# GET /v1/planes
# Lista los planes de suscripción disponibles.
@router.get(
    "",
    response_model=SubscriptionPlanListDocument,
    summary="Listar planes de subscripcion",
)
async def list_subscription_plans(
    current_user: UserResponse = Depends(get_current_active_user),
    offset: int = 0,
    limit: int = 10,
    use_case: ListSubscriptionPlansUseCase = Depends(get_list_subscription_plans_use_case),

) -> SubscriptionPlanListDocument:
    """Lista los planes de subscripcion."""
    res = await use_case.execute(offset, limit)
    return SubscriptionPlanListDocument(
        data=[
            SubscriptionPlanResource(
                id=p.id,
                attributes=SubscriptionPlanAttributes(
                    nombre=p.nombre,
                    descripcion=p.descripcion,
                    max_activos=p.max_activos,
                    max_usuarios=p.max_activos,
                    version=p.version,
                ),
            )
            for p in res
        ],
        meta={"total": len(res)},
    )


# GET /v1/planes/{plan_id}
@router.get(
    "/{plan_id}",
    response_model=SubscriptionPlanDocument,
    summary="Obtener planes por ID",
)
async def get_subscription_plan(
    plan_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    use_case: GetSubscriptionPlanUseCase = Depends(get_subscription_plan_use_case),
) -> SubscriptionPlanDocument:
    """Obtiene el plan de subscripcion."""
    res = await use_case.execute(plan_id)
    return SubscriptionPlanDocument(
        data=SubscriptionPlanResource(
            id=res.id,
            attributes=SubscriptionPlanAttributes(
            nombre=res.nombre,
            descripcion=res.descripcion,
            max_activos=res.max_activos,
            max_usuarios=res.max_activos,
            version=res.version,
            ),
        )
    )

# PATCH /v1/planes/{plan_id}
@router.patch(
    "/{plan_id}",
    response_model=SubscriptionPlanDocument,
    summary="Actualizar plan de subscripcion",
)
async def update_preferences(
    plan_id: str,
    request: UpdateSubscriptionPlanRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: UpdateSubscriptionPlanUseCase = Depends(get_update_subscription_plan_use_case),
) -> SubscriptionPlanDocument:
    """Actualiza las preferencias del usuario autenticado."""
    dto = UpdateSubscriptionPlanDTO(
        nombre=request.data.attributes.nombre,
        descripcion=request.data.attributes.descripcion,
        max_activos=request.data.attributes.max_activos,
        max_usuarios=request.data.attributes.max_usuarios,
        version=request.data.attributes.version
    )
    res = await use_case.execute(plan_id, dto)
    return SubscriptionPlanDocument(
        data=SubscriptionPlanResource(
            id=res.id,
            attributes=SubscriptionPlanAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                max_activos=res.max_activos,
                max_usuarios=res.max_activos,
                version=res.version,
            ),
        )
    )

@router.post (
    "",
    response_model=SubscriptionPlanDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo plan"
)
async def create_subscription_plan(
  request: CreateSubscriptionPlanRequest,
  current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "create")),
  use_case: CreateSubscriptionPlanUseCase = Depends(get_create_subscription_plan_use_case),
) -> SubscriptionPlanDocument:
    """Crea un nuevo plan de subscripcion."""
    dto = CreateSubscriptionPlanDTO(
        nombre=request.data.attributes.nombre,
        descripcion=request.data.attributes.descripcion,
        max_activos=request.data.attributes.max_activos,
        max_usuarios=request.data.attributes.max_usuarios,
        version=request.data.attributes.version
    )
    res = await use_case.execute(dto)
    return SubscriptionPlanDocument(
        data=SubscriptionPlanResource(
            id=res.id,
            attributes=SubscriptionPlanAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                max_activos=res.max_activos,
                max_usuarios=res.max_activos,
                version=res.version,
            ),
        )
    )

# DELETE /v1/planes/{plan_id}
@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar plan de subscripcion",
)
async def delete_subscription_plan(
    plan_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "delete")),
    use_case: DeleteSubscriptionPlanUseCase = Depends(get_delete_subscription_plan_use_case),
) -> None:
    """Elimina un plan de subscripcion."""
    await use_case.execute(plan_id)