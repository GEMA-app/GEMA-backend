"""Implementación SQLAlchemy para el repositorio de movimientos de inventario (InventoryEntry)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.inventory_entry_repository import InventoryEntryRepositoryPort
from app.domain.entities.inventory_entry import InventoryEntry
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId
from app.infrastructure.db.models.inventory_entry import InventoryEntryModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyInventoryEntryRepository(
    SqlAlchemyTenantRepository[InventoryEntryModel, InventoryEntry, UUID],
    InventoryEntryRepositoryPort,
):
    """Repositorio concreto utilizando SQLAlchemy para persistir movimientos de inventario."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, InventoryEntryModel, pending_events)
        self.pk_column = "id"

    def _to_entity(self, model: InventoryEntryModel) -> InventoryEntry:
        return InventoryEntry(
            id=model.id,
            empresa_id=CompanyId(model.empresa_id),
            repuesto_id=model.repuesto_id,
            ordenes_trabajo_id=model.ordenes_trabajo_id,
            usuario_id=model.usuario_id,
            cantidad=model.cantidad,
            tipo_movimiento=model.tipo_movimiento,
            precio_unitario=model.precio_unitario,
            moneda=model.moneda,
            fecha_movimiento=model.fecha_movimiento,
            observaciones=model.observaciones,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: InventoryEntry) -> InventoryEntryModel:
        return InventoryEntryModel(
            id=entity.id,
            empresa_id=entity.empresa_id.value,
            repuesto_id=entity.repuesto_id,
            ordenes_trabajo_id=entity.ordenes_trabajo_id,
            usuario_id=entity.usuario_id,
            cantidad=entity.cantidad,
            tipo_movimiento=entity.tipo_movimiento,
            precio_unitario=entity.precio_unitario,
            moneda=entity.moneda,
            fecha_movimiento=entity.fecha_movimiento,
            observaciones=entity.observaciones,
        )

    async def get_all_by_repuesto(
        self, repuesto_id: UUID, empresa_id: CompanyId, limit: int = 20, offset: int = 0
    ) -> list[InventoryEntry]:
        """Obtiene la lista paginada de movimientos asociados a un repuesto."""
        stmt = (
            select(self.model_class)
            .where(self.model_class.empresa_id == empresa_id.value)
            .where(self.model_class.repuesto_id == repuesto_id)
            .offset(offset)
            .limit(limit)
            .order_by(self.model_class.fecha_movimiento.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
