"""Adaptador SQLAlchemy para el repositorio de partes de inventario."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.inventory_part_repository import InventoryPartRepositoryPort
from app.domain.entities.inventory_part import InventoryPart
from app.domain.events import DomainEvent
from app.domain.exceptions.used_part import InsufficientStockError
from app.domain.value_objects import CompanyId, RepuestoId
from app.infrastructure.db.models.inventory_part import InventoryPartModel
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository


class SqlAlchemyInventoryPartRepository(
    SqlAlchemyTenantRepository[InventoryPartModel, InventoryPart, RepuestoId],
    InventoryPartRepositoryPort,
):
    """Implementación en SQLAlchemy para el repositorio de repuestos del inventario."""

    def __init__(
        self, session: AsyncSession, pending_events: list[DomainEvent] | None = None
    ) -> None:
        super().__init__(session, InventoryPartModel, pending_events)

    def _to_model(self, entity: InventoryPart) -> InventoryPartModel:
        return InventoryPartModel(
            id=entity.id.value,
            empresa_id=entity.empresa_id.value,
            articulo_id=entity.articulo_id.value,
            proveedor_id=entity.proveedor_id.value if entity.proveedor_id else None,
            stock_actual=entity.stock_actual,
            stock_minimo=entity.stock_minimo,
            ubicacion_almacen=entity.ubicacion_almacen,
            precio_unitario=entity.precio_unitario,
            moneda=entity.moneda,
            version=entity.version,
        )

    def _to_entity(self, model: InventoryPartModel) -> InventoryPart:
        from app.domain.value_objects import ArticleId, ProviderId

        return InventoryPart(
            id=RepuestoId(model.id),
            empresa_id=CompanyId(model.empresa_id),
            articulo_id=ArticleId(model.articulo_id),
            proveedor_id=(
                ProviderId(model.proveedor_id) if model.proveedor_id else ProviderId(UUID(int=0))
            ),
            stock_actual=model.stock_actual,
            stock_minimo=model.stock_minimo,
            ubicacion_almacen=model.ubicacion_almacen or "",
            precio_unitario=model.precio_unitario or Decimal("0"),
            moneda=model.moneda,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_all_by_company(
        self, empresa_id: CompanyId, limit: int = 20, offset: int = 0
    ) -> list[InventoryPart]:
        """Lista los repuestos de una empresa con paginación."""
        stmt = (
            select(InventoryPartModel)
            .where(InventoryPartModel.empresa_id == empresa_id.value)
            .offset(offset)
            .limit(limit)
            .order_by(InventoryPartModel.id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def validate_and_decrement_stock(
        self, repuesto_id: UUID, cantidad: int, empresa_id: CompanyId
    ) -> None:
        """Busca el repuesto en inventario, valida stock disponible y decrementa."""
        stmt = select(InventoryPartModel).where(
            InventoryPartModel.id == repuesto_id,
            InventoryPartModel.empresa_id == empresa_id.value,
        )
        res = await self.session.execute(stmt)
        inv_part = res.scalar_one_or_none()
        if inv_part is not None:
            if inv_part.stock_actual < cantidad:
                raise InsufficientStockError(
                    repuesto_id=str(repuesto_id),
                    disponible=inv_part.stock_actual,
                    solicitado=cantidad,
                )
            inv_part.stock_actual -= cantidad
