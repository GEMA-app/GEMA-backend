"""Caso de uso para delete subscription plan."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import (
    SubscriptionPlanHasActiveSubscriptionsError,
    SubscriptionPlanNotFoundError,
)
from app.domain.value_objects import SubscriptionPlanId


class DeleteSubscriptionPlanUseCase:
    """Caso de uso para eliminar un plan de suscripción."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(self, plan_id_str: str) -> None:
        """Elimina un plan de suscripción por su ID."""
        plan_id = SubscriptionPlanId.from_string(plan_id_str)
        async with self._uow:
            plan = await self._uow.subscription_plans.get_by_id(plan_id)
            if not plan:
                raise SubscriptionPlanNotFoundError(
                    f"El plan de suscripción con ID '{plan_id_str}' no existe."
                )

            active_companies = await self._uow.companies.count_by_plan_id(plan_id)
            if active_companies > 0:
                raise SubscriptionPlanHasActiveSubscriptionsError(
                    f"No se puede eliminar el plan '{plan.nombre}' porque está "
                    f"asignado a {active_companies} empresa(s)."
                )

            await self._uow.subscription_plans.delete(plan_id)
            await self._uow.commit()
