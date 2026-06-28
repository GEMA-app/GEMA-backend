"""Endpoints CRUD de planes de suscripción (plataforma, Super Admin)."""

from fastapi import APIRouter, Depends, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.subscription_plan_dtos import (
    CreateSubscriptionPlanRequest as CreateSubscriptionPlanDTO,
)
from app.application.dtos.subscription_plan_dtos import (
    UpdateSubscriptionPlanRequest as UpdateSubscriptionPlanDTO,
)
from app.application.use_cases.subscription_plan import (
    CreateSubscriptionPlanUseCase,
    DeleteSubscriptionPlanUseCase,
    GetSubscriptionPlanUseCase,
    ListSubscriptionPlansUseCase,
    UpdateSubscriptionPlanUseCase,
)
from app.composition.container import (
    get_create_subscription_plan_use_case,
    get_delete_subscription_plan_use_case,
    get_list_subscription_plans_use_case,
    get_subscription_plan_use_case,
    get_update_subscription_plan_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    get_current_active_user,
    require_platform_permission,
)
from app.presentation.api.v1.schemas.subscription_plan import (
    CreateSubscriptionPlanRequest,
    SubscriptionPlanAttributes,
    SubscriptionPlanDocument,
    SubscriptionPlanListDocument,
    SubscriptionPlanResource,
    UpdateSubscriptionPlanRequest,
)

router = APIRouter()


@router.get(
    "",
    response_model=SubscriptionPlanListDocument,
    summary="Listar planes de suscripción",
)
async def list_subscription_plans(
    current_user: UserResponse = Depends(get_current_active_user),
    offset: int = 0,
    limit: int = 10,
    use_case: ListSubscriptionPlansUseCase = Depends(get_list_subscription_plans_use_case),
) -> SubscriptionPlanListDocument:
    """Lista los planes de suscripción paginados."""
    responses, total = await use_case.execute(offset, limit)
    return SubscriptionPlanListDocument(
        data=[
            SubscriptionPlanResource(
                id=p.id,
                attributes=SubscriptionPlanAttributes(
                    nombre=p.nombre,
                    descripcion=p.descripcion,
                    precio_mensual_usd=p.precio_mensual_usd,
                    max_activos=p.max_activos,
                    max_usuarios=p.max_usuarios,
                    is_active=p.is_active,
                ),
            )
            for p in responses
        ],
        meta={"total": total},
    )


@router.get(
    "/{plan_id}",
    response_model=SubscriptionPlanDocument,
    summary="Obtener plan por ID",
)
async def get_subscription_plan(
    plan_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    use_case: GetSubscriptionPlanUseCase = Depends(get_subscription_plan_use_case),
) -> SubscriptionPlanDocument:
    """Obtiene un plan de suscripción por su ID."""
    res = await use_case.execute(plan_id)
    return SubscriptionPlanDocument(
        data=SubscriptionPlanResource(
            id=res.id,
            attributes=SubscriptionPlanAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                precio_mensual_usd=res.precio_mensual_usd,
                max_activos=res.max_activos,
                max_usuarios=res.max_usuarios,
                is_active=res.is_active,
            ),
        )
    )


@router.post(
    "",
    response_model=SubscriptionPlanDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear plan de suscripción",
)
async def create_subscription_plan(
    request: CreateSubscriptionPlanRequest,
    current_user: UserResponse = Depends(
        require_platform_permission(PermissionModule.ADMIN, "create")
    ),
    use_case: CreateSubscriptionPlanUseCase = Depends(get_create_subscription_plan_use_case),
) -> SubscriptionPlanDocument:
    """Crea un nuevo plan de suscripción."""
    attrs = request.data.attributes
    dto = CreateSubscriptionPlanDTO(
        nombre=attrs.nombre,
        descripcion=attrs.descripcion,
        precio_mensual_usd=attrs.precio_mensual_usd,
        max_activos=attrs.max_activos,
        max_usuarios=attrs.max_usuarios,
    )
    res = await use_case.execute(dto)
    return SubscriptionPlanDocument(
        data=SubscriptionPlanResource(
            id=res.id,
            attributes=SubscriptionPlanAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                precio_mensual_usd=res.precio_mensual_usd,
                max_activos=res.max_activos,
                max_usuarios=res.max_usuarios,
                is_active=res.is_active,
            ),
        )
    )


@router.patch(
    "/{plan_id}",
    response_model=SubscriptionPlanDocument,
    summary="Actualizar plan de suscripción",
)
async def update_subscription_plan(
    plan_id: str,
    request: UpdateSubscriptionPlanRequest,
    current_user: UserResponse = Depends(
        require_platform_permission(PermissionModule.ADMIN, "edit")
    ),
    use_case: UpdateSubscriptionPlanUseCase = Depends(get_update_subscription_plan_use_case),
) -> SubscriptionPlanDocument:
    """Actualiza un plan de suscripción existente."""
    attrs = request.data.attributes
    dto = UpdateSubscriptionPlanDTO(
        nombre=attrs.nombre,
        descripcion=attrs.descripcion,
        precio_mensual_usd=attrs.precio_mensual_usd,
        max_activos=attrs.max_activos,
        max_usuarios=attrs.max_usuarios,
        is_active=attrs.is_active,
    )
    res = await use_case.execute(plan_id, dto)
    return SubscriptionPlanDocument(
        data=SubscriptionPlanResource(
            id=res.id,
            attributes=SubscriptionPlanAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                precio_mensual_usd=res.precio_mensual_usd,
                max_activos=res.max_activos,
                max_usuarios=res.max_usuarios,
                is_active=res.is_active,
            ),
        )
    )


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar plan de suscripción",
)
async def delete_subscription_plan(
    plan_id: str,
    current_user: UserResponse = Depends(
        require_platform_permission(PermissionModule.ADMIN, "delete")
    ),
    use_case: DeleteSubscriptionPlanUseCase = Depends(get_delete_subscription_plan_use_case),
) -> None:
    """Elimina un plan de suscripción."""
    await use_case.execute(plan_id)
