"""Modelo ORM para la tabla articulos_catalogo."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.article_category import ArticleCategoryModel


class CatalogArticleModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM placeholder para los artículos del catálogo de la empresa."""

    __tablename__ = "articulos_catalogo"
    __table_args__ = (
        Index("idx_articulos_catalogo_empresa_categoria", "empresa_id", "categoria_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    categoria_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categorias_articulos.id", ondelete="SET NULL"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fabricante: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unidad_medida: Mapped[str | None] = mapped_column(String(50), nullable=True)

    categoria: Mapped[ArticleCategoryModel | None] = relationship(
        "ArticleCategoryModel", back_populates="articulos"
    )

