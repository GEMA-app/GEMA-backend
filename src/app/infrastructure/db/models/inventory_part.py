"""Modelo de datos de SQLAlchemy ORM para la tabla 'inventory_parts'."""
import enum
import uuid
from decimal import Decimal
from sqlalchemy import ForeignKey, Index, Numeric, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


# 1. El Enum debe ir arriba de los modelos para que ambos lo puedan usar
class MovementType(str, enum.Enum):
    ENTRY = "entrada"
    EXIT = "salida"


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

    # 2. Relación con la tabla de movimientos
    movimientos: Mapped[list["InventoryEntryModel"]] = relationship(
        "InventoryEntryModel", back_populates="repuesto", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<InventoryPartModel(id={self.id}, empresa_id={self.empresa_id}, "
            f"articulo_id={self.articulo_id}, stock_actual={self.stock_actual}, "
            f"version={self.version})>"
        )


# 3. Tu nuevo modelo al final de todo
class InventoryEntryModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Representación relacional estricta en PostgreSQL de los Movimientos de Inventario."""

    __tablename__ = "inventory_entries"
    
    __table_args__ = (
        Index("idx_inventory_entries_empresa_repuesto", "empresa_id", "repuesto_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    repuesto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventory_parts.id", ondelete="CASCADE"), nullable=False
    )
    
    movement_type: Mapped[MovementType] = mapped_column(
        Enum(MovementType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relación inversa
    repuesto: Mapped["InventoryPartModel"] = relationship(back_populates="movimientos")

    def __repr__(self) -> str:
        return (
            f"<InventoryEntryModel(id={self.id}, empresa_id={self.empresa_id}, "
            f"repuesto_id={self.repuesto_id}, movement_type={self.movement_type}, quantity={self.quantity})>"
        )