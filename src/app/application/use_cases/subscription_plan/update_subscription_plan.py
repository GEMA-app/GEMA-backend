"""Caso de uso para update subscription plan."""

from app.application.dtos.subscription_plan_dtos import (
    SubscriptionPlanResponse,
    UpdateSubscriptionPlanRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.subscription_plan import SubscriptionPlanNotFoundError
from app.domain.value_objects.identifier import SubscriptionPlanId


class UpdateSubscriptionPlanUseCase:
    """Caso de uso para actualizar un plan de suscripción."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(
        self, plan_id_str: str, request: UpdateSubscriptionPlanRequest
    ) -> SubscriptionPlanResponse:
        """Ejecuta el caso de uso para actualizar un plan de suscripción."""
        subscription_plan_id = SubscriptionPlanId.from_string(plan_id_str)

        async with self._uow:
            plan = await self._uow.subscription_plans.get_by_id(subscription_plan_id)
            if not plan:
                raise SubscriptionPlanNotFoundError(
                    f"Plan de suscripción con ID {plan_id_str} no encontrado."
                )

            if request.nombre is not None or request.descripcion is not None:
                nuevo_nombre = request.nombre if request.nombre is not None else plan.nombre
                nueva_desc = (
                    request.descripcion if request.descripcion is not None else plan.descripcion
                )
                plan.update_details(nuevo_nombre, nueva_desc)

            if request.precio_mensual_usd is not None:
                plan.update_pricing(request.precio_mensual_usd)

            if request.max_activos is not None or request.max_usuarios is not None:
                nuevo_max_activos = (
                    request.max_activos if request.max_activos is not None else plan.max_activos
                )
                nuevo_max_usuarios = (
                    request.max_usuarios if request.max_usuarios is not None else plan.max_usuarios
                )
                plan.update_limits(nuevo_max_activos, nuevo_max_usuarios)

            if request.is_active is not None:
                if request.is_active:
                    plan.activate()
                else:
                    plan.deactivate()

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
