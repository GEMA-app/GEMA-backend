"""Modelo de datos de SQLAlchemy ORM para la tabla 'inventory_parts'."""

import uuid
from decimal import Decimal
from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class InventoryPartModel(TenantMixin, TimestampMixin, Base):
    """Representación relacional estricta en PostgreSQL del Repuesto en Inventario (Multi-tenant)."""

    __tablename__ = "inventory_parts"
    __table_args__ = (
        Index("idx_inventory_parts_empresa_articulo", "empresa_id", "articulo_id"),
        Index("idx_inventory_parts_empresa_proveedor", "empresa_id", "proveedor_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # llaves foráneas y relaciones jerárquicas
    articulo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("articulos_catalogo.id", ondelete="RESTRICT"), nullable=False
    )
    proveedor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("proveedores.id", ondelete="RESTRICT"), nullable=False
    )
    
    # Campos de control de almacén y stock
    stock_actual: Mapped[int] = mapped_column(default=0, nullable=False)
    stock_minimo: Mapped[int] = mapped_column(default=0, nullable=False)
    ubicacion_almacen: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Datos financieros mapeados de manera exacta a Decimal
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2), default=Decimal("0.00"), nullable=False
    )
    moneda: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Campo requerido para la concurrencia optimista de la entidad
    version: Mapped[int] = mapped_column(default=1, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<InventoryPartModel(id={self.id}, empresa_id={self.empresa_id}, "
            f"articulo_id={self.articulo_id}, stock_actual={self.stock_actual}, "
            f"version={self.version})>"
        )