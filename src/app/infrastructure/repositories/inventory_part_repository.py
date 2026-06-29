"""Repositorio de repuestos de inventario con SQLAlchemy asíncrono."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.inventory_part_repository import InventoryPartRepositoryPort
from app.domain.entities.inventory_part import InventoryPart
from app.domain.events import DomainEvent
from app.domain.value_objects import CompanyId, InventoryPartId, ArticleId, ProviderId
from app.infrastructure.db.models.inventory_part import InventoryPartModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyInventoryPartRepository(
    SqlAlchemyTenantRepository[InventoryPartModel, InventoryPart, InventoryPartId],
    InventoryPartRepositoryPort
):
    """Implementación en SQLAlchemy para el puerto de repositorio de Repuestos de Inventario."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, InventoryPartModel, pending_events)

    def _to_model(self, entity: InventoryPart) -> InventoryPartModel:
        """Mapeador: Convierte la entidad de dominio a un modelo ORM para persistencia."""
        return InventoryPartModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            articulo_id=entity.articulo_id.value,
            proveedor_id=entity.proveedor_id.value,
            stock_actual=entity.stock_actual,
            stock_minimo=entity.stock_minimo,
            ubicacion_almacen=entity.ubicacion_almacen,
            precio_unitario=entity.precio_unitario,
            moneda=entity.moneda,
            version=entity.version,
        )

    def _to_entity(self, model: InventoryPartModel) -> InventoryPart:
        """Mapeador: Convierte el modelo ORM de base de datos a una entidad de dominio pura."""
        return InventoryPart(
            id=InventoryPartId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            articulo_id=ArticleId(model.articulo_id),
            proveedor_id=ProviderId(model.proveedor_id),
            stock_actual=model.stock_actual,
            stock_minimo=model.stock_minimo,
            ubicacion_almacen=model.ubicacion_almacen,
            precio_unitario=model.precio_unitario,
            moneda=model.moneda,
            version=model.version,
        )

    async def get_by_id(self, empresa_id: CompanyId, part_id: InventoryPartId) -> InventoryPart | None:
        """Recupera un repuesto por su ID garantizando aislamiento multi-tenant."""
        stmt = select(InventoryPartModel).where(
            InventoryPartModel.id == part_id.value,
            InventoryPartModel.empresa_id == empresa_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_by_empresa(
        self, empresa_id: CompanyId, limit: int = 20, offset: int = 0
    ) -> list[InventoryPart]:
        """Obtiene el listado paginado de repuestos de una empresa específica."""
        stmt = (
            select(InventoryPartModel)
            .where(InventoryPartModel.empresa_id == empresa_id.value)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]