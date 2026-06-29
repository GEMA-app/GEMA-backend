"""Repositorio SQLAlchemy para el modelo MaintenancePlan."""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.maintenance_plan_repository import MaintenancePlanRepositoryPort
from app.domain.entities.maintenance_plan import MaintenancePlan
from app.domain.enums import MaintenanceType
from app.domain.events import DomainEvent
from app.domain.value_objects import AssetId, CompanyId, MaintenancePlanId, UserId
from app.infrastructure.db.models.maintenance_plan import MaintenancePlanModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyMaintenancePlanRepository(
    SqlAlchemyTenantRepository[MaintenancePlanModel, MaintenancePlan, MaintenancePlanId],
    MaintenancePlanRepositoryPort,
):
    """Repositorio concreto para planes de mantenimiento."""

    pk_column = "id"

    def __init__(
        self,
        session: AsyncSession,
        pending_events: list[DomainEvent] | None = None,
    ) -> None:
        super().__init__(session, MaintenancePlanModel, pending_events)

    def _to_model(self, entity: MaintenancePlan) -> MaintenancePlanModel:
        return MaintenancePlanModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            activo_id=entity.activo_id.value,
            tecnico_responsable_id=(
                entity.tecnico_responsable_id.value if entity.tecnico_responsable_id else None
            ),
            nombre=entity.nombre,
            tipo=entity.tipo,
            intervalo_dias=entity.intervalo_dias,
            proxima_ejecucion=entity.proxima_ejecucion,
            descripcion_tareas=entity.descripcion_tareas,
            activo=entity.activo,
        )

    def _to_entity(self, model: MaintenancePlanModel) -> MaintenancePlan:
        return MaintenancePlan(
            id=MaintenancePlanId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            activo_id=AssetId(model.activo_id),
            nombre=model.nombre,
            tipo=MaintenanceType(model.tipo),
            intervalo_dias=model.intervalo_dias,
            proxima_ejecucion=model.proxima_ejecucion,
            tecnico_responsable_id=(
                UserId(model.tecnico_responsable_id) if model.tecnico_responsable_id else None
            ),
            descripcion_tareas=model.descripcion_tareas,
            activo=model.activo,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_all_by_company(
        self,
        company_id: CompanyId,
        offset: int = 0,
        limit: int = 20,
        filters: dict[str, object] | None = None,
    ) -> tuple[Sequence[MaintenancePlan], int]:
        """Lista los planes de mantenimiento de una empresa con paginación.

        Args:
            company_id (CompanyId): Identificador de la empresa.
            offset (int): Número de registros a omitir.
            limit (int): Máximo de registros por página.
            filters (dict[str, object] | None): Filtros opcionales por activo_id, tipo, activo.

        Returns:
            tuple[Sequence[MaintenancePlan], int]: Tupla con la lista de entidades y el total.
        """
        filters = filters or {}
        # Consulta base filtrada por tenant
        base = select(MaintenancePlanModel).where(
            MaintenancePlanModel.empresa_id == company_id.value
        )
        count_q = select(func.count()).select_from(MaintenancePlanModel).where(
            MaintenancePlanModel.empresa_id == company_id.value
        )

        # Aplica filtros opcionales tanto a la query de datos como al count
        if "activo_id" in filters:
            cond = MaintenancePlanModel.activo_id == filters["activo_id"]
            base = base.where(cond)
            count_q = count_q.where(cond)
        if "tipo" in filters:
            cond = MaintenancePlanModel.tipo == filters["tipo"]
            base = base.where(cond)
            count_q = count_q.where(cond)
        if "activo" in filters:
            cond = MaintenancePlanModel.activo == filters["activo"]
            base = base.where(cond)
            count_q = count_q.where(cond)

        base = base.offset(offset).limit(limit)
        result = await self.session.execute(base)
        models = result.scalars().all()

        total_result = await self.session.execute(count_q)
        total = total_result.scalar_one()

        return [self._to_entity(m) for m in models], total

    async def save(self, plan: MaintenancePlan) -> MaintenancePlan:  # type: ignore[override]
        """Persiste un nuevo plan y retorna la entidad con datos actualizados.

        Args:
            plan (MaintenancePlan): Entidad del plan a persistir.

        Returns:
            MaintenancePlan: Entidad con datos actualizados (id generado, version, etc.).
        """
        model = self._to_model(plan)
        # merge() maneja tanto entidades transient como detached
        merged = await self.session.merge(model)
        await self.session.flush()
        self._collect_events(plan)
        return self._to_entity(merged)

    async def update(self, plan: MaintenancePlan) -> MaintenancePlan:
        """Actualiza un plan existente y retorna la entidad actualizada.

        Args:
            plan (MaintenancePlan): Entidad con los campos modificados.

        Returns:
            MaintenancePlan: Entidad actualizada con datos refrescados de BD.
        """
        model = self._to_model(plan)
        merged = await self.session.merge(model)
        await self.session.flush()
        self._collect_events(plan)
        return self._to_entity(merged)
