"""Modelo ORM de SQLAlchemy para la tabla de inventario de repuestos."""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.catalog_article import CatalogArticleModel
    from app.infrastructure.db.models.supplier import SupplierModel


class InventoryPartModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de inventario de repuestos (`inventario_repuestos`)."""

    __tablename__ = "inventario_repuestos"
    __table_args__ = (
        Index("ix_inventario_repuestos_empresa_articulo", "empresa_id", "articulo_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    articulo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("articulos_catalogo.id", ondelete="RESTRICT"), nullable=False
    )
    proveedor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("proveedores.id", ondelete="SET NULL"), nullable=True
    )
    stock_actual: Mapped[int] = mapped_column(default=0, nullable=False)
    stock_minimo: Mapped[int] = mapped_column(default=0, nullable=False)
    ubicacion_almacen: Mapped[str | None] = mapped_column(String(255), nullable=True)
    precio_unitario: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # Relaciones
    articulo: Mapped["CatalogArticleModel"] = relationship("CatalogArticleModel")
    proveedor: Mapped["SupplierModel | None"] = relationship("SupplierModel")
