"""Repositorio de Planes de Suscripción implementado con SQLAlchemy asíncrono."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.subscription_plan_repository import SubscriptionPlanRepositoryPort
from app.domain.entities import SubscriptionPlan
from app.domain.events import DomainEvent
from app.domain.value_objects import SubscriptionPlanId
from app.infrastructure.db.models.subscription_plan import SubscriptionPlanModel
from app.infrastructure.repositories.base import SqlAlchemyRepository


class SqlAlchemySubscriptionPlanRepository(
    SqlAlchemyRepository[SubscriptionPlanModel, SubscriptionPlan, SubscriptionPlanId],
    SubscriptionPlanRepositoryPort,
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Planes de Suscripción."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, SubscriptionPlanModel, pending_events)

    def _to_model(self, entity: SubscriptionPlan) -> SubscriptionPlanModel:
        return SubscriptionPlanModel(
            id=entity.id.value,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
            max_activos=entity.max_activos,
            max_usuarios=entity.max_usuarios,
            precio_mensual_usd=entity.precio_mensual_usd,
            is_active=entity.is_active,
        )

    def _to_entity(self, model: SubscriptionPlanModel) -> SubscriptionPlan:
        return SubscriptionPlan(
            id=SubscriptionPlanId(model.id),
            nombre=model.nombre,
            descripcion=model.descripcion,
            max_activos=model.max_activos,
            max_usuarios=model.max_usuarios,
            precio_mensual_usd=model.precio_mensual_usd,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(
        self, plan_id: SubscriptionPlanId
    ) -> SubscriptionPlan | None:
        """Obtiene un plan por su ID.

        Returns:
            La entidad SubscriptionPlan si existe, None en caso contrario.
        """
        stmt = select(self.model_class).where(self.model_class.id == plan_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> SubscriptionPlan | None:
        """Obtiene un plan por su nombre.

        Returns:
            La entidad SubscriptionPlan si existe, None en caso contrario.
        """
        stmt = select(self.model_class).where(self.model_class.nombre == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_active_plans(self) -> list[SubscriptionPlan]:
        """Lista todos los planes activos.

        Returns:
            Lista de entidades SubscriptionPlan activas.
        """
        stmt = select(self.model_class).where(self.model_class.is_active)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_all_plans(
        self, offset: int, limit: int
    ) -> tuple[list[SubscriptionPlan], int]:
        """Lista todos los planes paginados.

        Returns:
            Tupla con la lista de planes y el total de registros.
        """
        stmt = select(self.model_class).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        count_stmt = select(func.count()).select_from(self.model_class)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        return [self._to_entity(m) for m in models], total
