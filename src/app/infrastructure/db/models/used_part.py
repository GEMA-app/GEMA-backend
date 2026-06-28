"""Modelo ORM para la tabla used_parts (repuestos_utilizados)."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class UsedPartModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM que mapea la tabla 'repuestos_utilizados'."""

    __tablename__ = "repuestos_utilizados"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    intervencion_id: Mapped[UUID] = mapped_column(nullable=False)
    repuesto_id: Mapped[UUID] = mapped_column(nullable=False)
    cantidad_usada: Mapped[int] = mapped_column(nullable=False)
    precio_unitario: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    moneda: Mapped[str] = mapped_column(String(3), default="USD")
