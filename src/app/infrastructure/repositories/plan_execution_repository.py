"""Repositorio SQLAlchemy para la entidad PlanExecution."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.plan_execution_repository import PlanExecutionRepositoryPort
from app.domain.entities.plan_execution import PlanExecution
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, PlanExecutionId
from app.infrastructure.db.models.plan_execution import PlanExecutionModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyPlanExecutionRepository(
    SqlAlchemyTenantRepository[PlanExecutionModel, PlanExecution, PlanExecutionId],
    PlanExecutionRepositoryPort,
):
    """Repositorio SQLAlchemy para persistir ejecuciones de plan."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, PlanExecutionModel, pending_events)

    def _to_model(self, entity: PlanExecution) -> PlanExecutionModel:
        """Convierte entidad de dominio a modelo ORM."""
        return PlanExecutionModel(
            id=UUID(str(entity.id)),
            empresa_id=UUID(str(entity.empresa_id)),
            plan_id=entity.plan_id,
            work_order_id=UUID(str(entity.work_order_id)),
            execution_date=entity.execution_date,
            observations=entity.observations,
        )


    def _to_entity(self, model: PlanExecutionModel) -> PlanExecution:
        """Convierte modelo ORM a entidad de dominio."""
        return PlanExecution(
            id=PlanExecutionId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            plan_id=model.plan_id,
            work_order_id=model.work_order_id,
            execution_date=model.execution_date,
            observations=model.observations,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_plan_id(
        self, plan_id: UUID, empresa_id: CompanyId
    ) -> list[PlanExecution]:
        """Lista ejecuciones por plan y empresa.

        Args:
            plan_id: ID del plan de mantenimiento.
            empresa_id: ID de la empresa.

        Returns:
            Lista de entidades PlanExecution.
        """
        stmt = (
            select(PlanExecutionModel)
            .where(
                PlanExecutionModel.plan_id == plan_id,
                PlanExecutionModel.empresa_id == UUID(str(empresa_id)),
            )
            .order_by(PlanExecutionModel.execution_date.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, execution: PlanExecution) -> PlanExecution:  # type: ignore[override]
        """Persiste una ejecución de plan.

        Args:
            execution: Entidad PlanExecution a persistir.

        Returns:
            La entidad persistida.
        """
        model = self._to_model(execution)
        merged = await self.session.merge(model)
        self._collect_events(execution)
        return self._to_entity(merged)
