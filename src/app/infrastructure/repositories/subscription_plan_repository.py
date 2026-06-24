
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.subscription_plan_repository import SubscriptionPlanPort
from app.domain.entities import SubscriptionPlan
from app.domain.events import DomainEvent
from app.domain.value_objects import SubscriptionPlanId
from app.infrastructure.db.models.subscription_plan import SubscriptionPlanModel
from app.infrastructure.repositories.base import SqlAlchemyRepository

class SqlAlchemySubscriptionPlanRepository(
    SqlAlchemyRepository[SubscriptionPlanModel, SubscriptionPlan, SubscriptionPlanId],
    SubscriptionPlanPort,
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Planes de Suscripción."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        """Inicializa el repositorio de planes de suscripción con la sesión de base de datos.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
            pending_events: Lista para la acumulación de eventos de dominio.
        """
        super().__init__(session, SubscriptionPlanModel, pending_events)

    def _to_model(self, entity: SubscriptionPlan) -> SubscriptionPlanModel:
        return SubscriptionPlanModel(
            id=entity.id.value,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
            max_activos=entity.max_activos,
            max_usuarios=entity.max_usuarios,
            precio_mensual_usd=entity.precio_mensual_usd,
            # start_date=entity.start_date,
            # end_date=entity.end_date,
            is_active=entity.is_active,
            version=entity.version,
        )
    
    def _to_entity(self, model: SubscriptionPlanModel) -> SubscriptionPlan:
        return SubscriptionPlan(
            id=SubscriptionPlanId(model.id),
            nombre=model.nombre,
            descripcion=model.descripcion,
            max_activos=model.max_activos,
            max_usuarios=model.max_usuarios,
            precio_mensual_usd=model.precio_mensual_usd,
            # start_date=model.start_date,
            # end_date=model.end_date,
            is_active=model.is_active,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    async def get_by_id(self, plan_id: SubscriptionPlanId):
        """Genera la consulta para obtener un plan de suscripción por su ID."""
        stmt = select(self.model_class).where(self.model_class.id == plan_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str):
        """Genera la consulta para obtener un plan de suscripción por su nombre."""
        stmt = select(self.model_class).where(self.model_class.nombre == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_active_plans(self):
        """Genera la consulta para listar todos los planes de suscripción activos."""
        stmt = select(self.model_class).where(self.model_class.is_active == True)
        result = await self.session.execute(stmt)
        if not result.scalars().all():
            return []
        return [self._to_entity(model) for model in result.scalars()]

    async def list_all_plans(self):
        """Genera la consulta para listar todos los planes de suscripción, activos e inactivos."""
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars()]
