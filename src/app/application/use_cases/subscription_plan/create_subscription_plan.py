from app.application.dtos.subscription_plan_dtos import CreateSubscriptionPlanRequest, SubscriptionPlanResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import SubscriptionPlan
from app.domain.exceptions import SubscriptionPlanAlreadyExistsError

class CreateSubscriptionPlanUseCase:
    """Caso de uso para crear un nuevo plan de suscripción."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, request: CreateSubscriptionPlanRequest) -> SubscriptionPlanResponse:
        """Crea un nuevo plan de suscripción y lo persiste."""
        async with self.uow:
            # Validar que no exista un plan con el mismo nombre
            existing_plan = await self.uow.subscription_plans.get_by_name(request.nombre)
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
                # start_date=request.start_date,
                # end_date=request.end_date,
                is_active=True,  # Por defecto, el plan se crea como activo
            )
            await self.uow.subscription_plans.save(plan)
            await self.uow.commit()

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
                version=plan.version,
            )