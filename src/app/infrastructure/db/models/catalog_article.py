"""Modelo ORM para artículos del catálogo (articulos_catalogo)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.infrastructure.db.models.article_category import ArticleCategoryModel

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin

# ---------------------------------------------------------------------------
# Constantes de longitudes máximas de columnas
# ---------------------------------------------------------------------------
_MAX_ARTICLE_NAME_LENGTH: int = 255
_MAX_MANUFACTURER_LENGTH: int = 100
_MAX_MODEL_LENGTH: int = 100
_MAX_UNIT_OF_MEASURE_LENGTH: int = 50


class CatalogArticleModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para los artículos del catálogo de la empresa."""

    __tablename__ = "articulos_catalogo"
    __table_args__ = (
        Index("idx_articulos_catalogo_empresa_categoria", "empresa_id", "categoria_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        "categoria_id",
        ForeignKey("categorias_articulos.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column("nombre", String(_MAX_ARTICLE_NAME_LENGTH), nullable=False)
    description: Mapped[str | None] = mapped_column("descripcion", Text, nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(
        "fabricante", String(_MAX_MANUFACTURER_LENGTH), nullable=True
    )
    model: Mapped[str | None] = mapped_column("modelo", String(_MAX_MODEL_LENGTH), nullable=True)
    unit_of_measure: Mapped[str | None] = mapped_column(
        "unidad_medida", String(_MAX_UNIT_OF_MEASURE_LENGTH), nullable=True
    )

    categoria: Mapped[ArticleCategoryModel | None] = relationship(
        "ArticleCategoryModel", back_populates="articulos"
    )
