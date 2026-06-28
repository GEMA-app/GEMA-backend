from app.application.dtos.subscription_plan_dtos import SubscriptionPlanResponse
from app.application.ports.unit_of_work import UnitOfWorkPort


class ListSubscriptionPlansUseCase:
    """Caso de uso para listar planes de suscripción paginados."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self._uow = uow

    async def execute(self, offset: int, limit: int) -> tuple[list[SubscriptionPlanResponse], int]:
        """Lista planes de suscripción paginados."""
        async with self._uow:
            plans, total = await self._uow.subscription_plans.list_all_plans(offset, limit)
            responses = [
                SubscriptionPlanResponse(
                    id=str(plan.id),
                    nombre=plan.nombre,
                    descripcion=plan.descripcion,
                    max_activos=plan.max_activos,
                    max_usuarios=plan.max_usuarios,
                    precio_mensual_usd=plan.precio_mensual_usd,
                    is_active=plan.is_active,
                )
                for plan in plans
            ]
            return responses, total
