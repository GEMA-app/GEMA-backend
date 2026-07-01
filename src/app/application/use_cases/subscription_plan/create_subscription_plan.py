"""Caso de uso para create subscription plan."""
from app.application.dtos.subscription_plan_dtos import (
    CreateSubscriptionPlanRequest,
    SubscriptionPlanResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import SubscriptionPlan
from app.domain.exceptions import SubscriptionPlanAlreadyExistsError


class CreateSubscriptionPlanUseCase:
    """Caso de uso para crear un nuevo plan de suscripción."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(self, request: CreateSubscriptionPlanRequest) -> SubscriptionPlanResponse:
        """Crea un nuevo plan de suscripción y lo persiste."""
        async with self._uow:
            existing_plan = await self._uow.subscription_plans.get_by_name(request.nombre)
            if existing_plan:
                raise SubscriptionPlanAlreadyExistsError(
                    f"Ya existe un plan de suscripción con el nombre '{request.nombre}'."
                )

            plan = SubscriptionPlan.create(
                nombre=request.nombre,
                descripcion=request.descripcion,
                max_activos=request.max_activos,
                max_usuarios=request.max_usuarios,
                precio_mensual_usd=request.precio_mensual_usd,
            )
            await self._uow.subscription_plans.save(plan)
            await self._uow.commit()

            return SubscriptionPlanResponse(
                id=str(plan.id),
                nombre=plan.nombre,
                descripcion=plan.descripcion,
                max_activos=plan.max_activos,
                max_usuarios=plan.max_usuarios,
                precio_mensual_usd=plan.precio_mensual_usd,
                is_active=plan.is_active,
            )
