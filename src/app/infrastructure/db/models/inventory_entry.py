"""Modelo ORM de SQLAlchemy para la tabla de entradas y movimientos de inventario."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.inventory_part import InventoryPartModel
    from app.infrastructure.db.models.user import UserModel
    from app.infrastructure.db.models.work_order import WorkOrderModel


class InventoryEntryModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de movimientos de inventario (`entradas_inventario`)."""

    __tablename__ = "entradas_inventario"
    __table_args__ = (
        Index("ix_entradas_inventario_empresa_repuesto", "empresa_id", "repuesto_id"),
        Index("ix_entradas_inventario_empresa_ot", "empresa_id", "ordenes_trabajo_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    repuesto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventario_repuestos.id", ondelete="CASCADE"), nullable=False
    )
    ordenes_trabajo_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ordenes_trabajo.id", ondelete="SET NULL"), nullable=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    cantidad: Mapped[int] = mapped_column(nullable=False)
    tipo_movimiento: Mapped[str] = mapped_column(String(50), nullable=False)  # entrada | salida
    precio_unitario: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    fecha_movimiento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    repuesto: Mapped["InventoryPartModel"] = relationship("InventoryPartModel")
    orden_trabajo: Mapped["WorkOrderModel | None"] = relationship("WorkOrderModel")
    usuario: Mapped["UserModel | None"] = relationship("UserModel")
