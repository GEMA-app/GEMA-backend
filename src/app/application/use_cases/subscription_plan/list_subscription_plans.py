from app.application.dtos.subscription_plan_dtos import SubscriptionPlanResponse
from app.application.ports.unit_of_work import UnitOfWorkPort

class ListSubscriptionPlansUseCase:
    """Caso de uso para listar planes de suscripción paginados."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, offset: int, limit: int) -> tuple[list[SubscriptionPlanResponse], int]:
        """Lista planes de suscripción paginados."""
        async with self.uow:
            plans, total = await self.uow.subscription_plans.list_all(offset, limit)
            responses = [
                SubscriptionPlanResponse(
                    id=str(plan.id),
                    nombre=plan.nombre,
                    descripcion=plan.descripcion,
                    max_activos=plan.max_activos,
                    max_usuarios=plan.max_usuarios,
                    precio_mensual_usd=plan.precio_mensual_usd,
                    # start_date=plan.start_date.isoformat(),
                    # end_date=plan.end_date.isoformat(),
                    is_active=plan.is_active,
                    version=plan.version,
                )
                for plan in plans
            ]
            return responses, total