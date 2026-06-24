from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.dtos.subscription_plan_dtos import SubscriptionPlanResponse
from app.domain.exceptions.subscription_plan import SubscriptionPlanNotFoundError
from app.domain.value_objects.identifier import SubscriptionPlanId

class GetSubscriptionPlanUseCase:
    """Caso de uso para obtener un plan de suscripción por su identificador."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, plan_id_str: str) -> SubscriptionPlanResponse:
        """Ejecuta el caso de uso para obtener un plan de suscripción."""

        subscription_plan_id = SubscriptionPlanId.from_string(plan_id_str)

        async with self.uow:
            plan = await self.uow.subscription_plans.get_by_id(subscription_plan_id)
            if not plan:
                raise SubscriptionPlanNotFoundError(f"Plan de suscripción con ID {plan_id_str} no encontrado.")
        
        return SubscriptionPlanResponse(
            id=str(plan.id),
            nombre=plan.nombre,
            descripcion=plan.descripcion,
            max_activos=plan.max_activos,
            max_usuarios=plan.max_usuarios,
            precio_mensual_usd=plan.precio_mensual_usd,
            # start_date=plan.start_date.isoformat(),
            # end_date=plan.end_date.isoformat(),
            is_active=plan.is_active,
            version=plan.version
        )