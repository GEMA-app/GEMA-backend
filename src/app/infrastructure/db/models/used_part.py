"""Modelo ORM para la tabla used_parts (repuestos_utilizados)."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class UsedPartModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM que mapea la tabla 'repuestos_utilizados'."""

    __tablename__ = "repuestos_utilizados"
    __table_args__ = (
        Index("ix_repuestos_utilizados_empresa_intervencion", "empresa_id", "intervencion_id"),
        Index("ix_repuestos_utilizados_empresa_repuesto", "empresa_id", "repuesto_id"),
    )


    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    intervencion_id: Mapped[UUID] = mapped_column(
        ForeignKey("intervenciones_tecnicas.id", ondelete="CASCADE"), nullable=False
    )
    repuesto_id: Mapped[UUID] = mapped_column(
        ForeignKey("inventario_repuestos.id", ondelete="RESTRICT"), nullable=False
    )

    cantidad_usada: Mapped[int] = mapped_column(nullable=False)
    precio_unitario: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    moneda: Mapped[str] = mapped_column(String(3), default="USD")
