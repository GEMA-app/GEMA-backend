"""Adaptador SQLAlchemy para el repositorio de partes de inventario."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.inventory_part_repository import InventoryPartRepositoryPort
from app.domain.exceptions.used_part import InsufficientStockError
from app.domain.value_objects import CompanyId
from app.infrastructure.db.models.inventory_part import InventoryPartModel


class SqlAlchemyInventoryPartRepository(InventoryPartRepositoryPort):
    """Implementación de persistencia para consultar y actualizar stock."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
