import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.infrastructure.db.models.catalog import CatalogArticleModel
    from app.infrastructure.db.models.location import LocationModel

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import AssetStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class AssetModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de activos físicos."""

    __tablename__ = "activos"
    __table_args__ = (
        UniqueConstraint("empresa_id", "serial_interno", name="uq_activos_empresa_serial_interno"),
        UniqueConstraint("empresa_id", "codigo_activo", name="uq_activos_empresa_codigo_activo"),
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
    valor_monetario: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # Relaciones
    articulo: Mapped["CatalogArticleModel"] = relationship("CatalogArticleModel")
    ubicacion: Mapped[Optional["LocationModel"]] = relationship("LocationModel")
