"""Modelo ORM para la tabla categorias_articulos."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.infrastructure.db.models.catalog import CatalogArticleModel

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class ArticleCategoryModel(Base, TenantMixin, TimestampMixin, VersionMixin):
    """Modelo ORM para la tabla categorias_articulos.

    Incluye VersionMixin para optimistic locking, TimestampMixin para
    created_at/updated_at, y TenantMixin para multi-tenancy por empresa_id.
    """

    __tablename__ = "categorias_articulos"
    __table_args__ = (
        UniqueConstraint(
            "empresa_id", "nombre", name="uq_categorias_articulos_empresa_nombre"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    articulos: Mapped[list[CatalogArticleModel]] = relationship(
        "CatalogArticleModel",
        back_populates="categoria",
        cascade="save-update, merge",
    )

