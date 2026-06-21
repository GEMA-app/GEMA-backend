"""Modelo ORM de SQLAlchemy para la tabla de activos físicos."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.db.models.catalog import CatalogArticleModel
    from app.infrastructure.db.models.location import LocationModel
    from app.infrastructure.db.models.asset_state_log import AssetStateLogModel

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import AssetStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class AssetModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de activos físicos."""

    __tablename__ = "activos"
    __table_args__ = (
        Index(
            "uq_activos_empresa_codigo_activo_lower",
            "empresa_id",
            text("LOWER(codigo_activo)"),
            unique=True,
        ),
        Index(
            "uq_activos_empresa_serial_interno_lower",
            "empresa_id",
            text("LOWER(serial_interno)"),
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    articulo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("articulos_catalogo.id", ondelete="RESTRICT"), nullable=False
    )
    ubicacion_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ubicaciones.id", ondelete="SET NULL"), nullable=True
    )
    serial_interno: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo_activo: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=AssetStatus.OPERATIONAL,
        nullable=False,
    )
    fecha_adquisicion: Mapped[date | None] = mapped_column(Date, nullable=True)
    valor_monetario: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    articulo: Mapped[CatalogArticleModel] = relationship("CatalogArticleModel")
    ubicacion: Mapped[LocationModel | None] = relationship("LocationModel")
state_logs: Mapped[list[AssetStateLogModel]] = relationship(back_populates="asset", cascade="all, delete-orphan")
