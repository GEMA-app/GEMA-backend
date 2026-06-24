from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import SubscriptionPlanNotFoundError
from app.domain.value_objects import SubscriptionPlanId

class DeleteSubscriptionPlanUseCase:
    """Caso de uso para eliminar un plan de suscripción."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, plan_id_str: str) -> None:
        """Elimina un plan de suscripción por su ID."""
        plan_id = SubscriptionPlanId.from_string(plan_id_str)
        async with self.uow:
            plan = await self.uow.subscription_plans.get_by_id(plan_id)
            if not plan:
                raise SubscriptionPlanNotFoundError(f"El plan de suscripción con ID '{plan_id_str}' no existe.")

            await self.uow.subscription_plans.delete(plan_id)
            await self.uow.commit()