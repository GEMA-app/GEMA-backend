"""Repositorio concreto para intervenciones tÃ©cnicas."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.intervention_repository import InterventionRepositoryPort
from app.domain.entities.intervention import TechnicalIntervention
from app.domain.events import DomainEvent
from app.domain.value_objects.identifier import CompanyId, InterventionId, UserId, WorkOrderId
from app.infrastructure.db.models.technical_intervention import TechnicalInterventionModel as InterventionModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyInterventionRepository(
    SqlAlchemyTenantRepository[InterventionModel, TechnicalIntervention, InterventionId],
    InterventionRepositoryPort,
):
    """ImplementaciÃ³n SQLAlchemy del repositorio de intervenciones."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, InterventionModel, pending_events)
        self.pk_column = "id"

    def _to_entity(self, model: InterventionModel) -> TechnicalIntervention:
        """Convierte un modelo ORM a una entidad de dominio.

        Args:
            model: Instancia del modelo ORM InterventionModel.

        Returns:
            Entidad de dominio TechnicalIntervention.
        """
        return TechnicalIntervention(
            id=InterventionId.from_string(str(model.id)),
            empresa_id=CompanyId.from_string(str(model.empresa_id)),
            work_order_id=WorkOrderId.from_string(str(model.ordenes_trabajo_id)),
            technician_id=UserId.from_string(str(model.tecnico_id)),
            tareas_realizadas=model.tareas_realizadas,
            fecha_inicio=model.fecha_inicio,
            fecha_fin=model.fecha_fin,
            horas_hombre=float(model.horas_hombre),
        )

    def _to_model(self, entity: TechnicalIntervention) -> InterventionModel:
        """Convierte una entidad de dominio a un modelo ORM.

        Args:
            entity: Entidad de dominio TechnicalIntervention.

        Returns:
            Instancia del modelo ORM InterventionModel.
        """
        return InterventionModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            ordenes_trabajo_id=entity.work_order_id.value,
            tecnico_id=entity.technician_id.value,
            tareas_realizadas=entity.tareas_realizadas,
            fecha_inicio=entity.fecha_inicio,
            fecha_fin=entity.fecha_fin,
            horas_hombre=entity.horas_hombre,
        )

    async def get_by_work_order(
        self,
        work_order_id: WorkOrderId,
        empresa_id: CompanyId,
    ) -> list[TechnicalIntervention]:
        """Obtiene todas las intervenciones de una orden de trabajo.

        Args:
            work_order_id: Identificador de la orden de trabajo.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            Lista de intervenciones asociadas a la orden de trabajo.
        """
        stmt = (
            select(InterventionModel)
            .where(InterventionModel.ordenes_trabajo_id == work_order_id.value)
            .where(InterventionModel.empresa_id == empresa_id.value)
            .order_by(InterventionModel.fecha_inicio.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_technician(
        self,
        technician_id: UserId,
        empresa_id: CompanyId,
    ) -> list[TechnicalIntervention]:
        """Obtiene todas las intervenciones realizadas por un tÃ©cnico.

        Args:
            technician_id: Identificador del tÃ©cnico.
            empresa_id: Identificador de la empresa (tenant).

        Returns:
            Lista de intervenciones realizadas por el tÃ©cnico.
        """
        stmt = (
            select(InterventionModel)
            .where(InterventionModel.tecnico_id == technician_id.value)
            .where(InterventionModel.empresa_id == empresa_id.value)
            .order_by(InterventionModel.fecha_inicio.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list(
        self,
        empresa_id: CompanyId,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[TechnicalIntervention], int]:
        """Lista todas las intervenciones de una empresa con paginaciÃ³n.

        Args:
            empresa_id: Identificador de la empresa.
            offset: NÃºmero de registros a omitir.
            limit: Cantidad mÃ¡xima de registros a retornar.

        Returns:
            Una tupla con la lista de intervenciones y el total de registros.
        """
        count_stmt = select(func.count()).select_from(InterventionModel).where(
            InterventionModel.empresa_id == empresa_id.value
        )
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(InterventionModel)
            .where(InterventionModel.empresa_id == empresa_id.value)
            .order_by(InterventionModel.fecha_inicio.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total
