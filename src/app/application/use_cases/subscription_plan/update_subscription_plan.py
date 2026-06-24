from app.application.dtos.subscription_plan_dtos import (
    UpdateSubscriptionPlanRequest, 
    SubscriptionPlanResponse 
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.subscription_plan import SubscriptionPlanNotFoundError
from app.domain.value_objects.identifier import SubscriptionPlanId

class UpdateSubscriptionPlanUseCase:
    """Caso de uso para actualizar un plan de suscripción."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, 
        plan_id_str: str,
        request: UpdateSubscriptionPlanRequest
    ) -> SubscriptionPlanResponse:
        """Ejecuta el caso de uso para actualizar un plan de suscripción."""
        subscription_plan_id = SubscriptionPlanId.from_string(plan_id_str)

        async with self.uow:
            plan = await self.uow.subscription_plans.get_by_id(subscription_plan_id)
            if not plan:
                raise SubscriptionPlanNotFoundError(f"Plan de suscripción con ID {plan_id_str} no encontrado.")

            # Actualizar los atributos del plan según la solicitud
            if request.nombre is not None:
                plan.update_details(request.nombre, request.descripcion)
            if request.precio_mensual_usd is not None:
                plan.update_pricing(request.precio_mensual_usd)
            if request.max_activos is not None and request.max_usuarios is not None:
                plan.update_limits(request.max_activos, request.max_usuarios)
            if request.start_date is not None and request.end_date is not None:
                plan.update_dates(request.start_date, request.end_date)
            if request.is_active is not None:
                plan.update_status(request.is_active)

            await self.uow.subscription_plans.save(plan)
            await self.uow.commit()

        return SubscriptionPlanResponse(
            id=str(plan.id),
            nombre=plan.nombre,
            descripcion=plan.descripcion,
            max_activos=plan.max_activos,
            max_usuarios=plan.max_usuarios,
            precio_mensual_usd=plan.precio_mensual_usd,
            start_date=plan.start_date.isoformat(),
            end_date=plan.end_date.isoformat(),
            is_active=plan.is_active,
            version=plan.version
        )