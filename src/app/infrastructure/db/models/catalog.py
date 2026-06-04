import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class ArticleCategoryModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM placeholder para las categorías de artículos del catálogo."""

    __tablename__ = "categorias_articulos"
    __table_args__ = (
        UniqueConstraint("empresa_id", "nombre", name="uq_categorias_articulos_empresa_nombre"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relación con artículos del catálogo
    articulos: Mapped[list["CatalogArticleModel"]] = relationship(
        "CatalogArticleModel",
        back_populates="categoria",
        cascade="all, delete-orphan"
    )


class CatalogArticleModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM placeholder para los artículos del catálogo de la empresa."""

    __tablename__ = "articulos_catalogo"
    __table_args__ = (
        Index("idx_articulos_catalogo_empresa_categoria", "empresa_id", "categoria_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categorias_articulos.id", ondelete="SET NULL"),
        nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fabricante: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    modelo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    unidad_medida: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relación con la categoría
    categoria: Mapped[Optional[ArticleCategoryModel]] = relationship(
        "ArticleCategoryModel",
        back_populates="articulos"
    )
