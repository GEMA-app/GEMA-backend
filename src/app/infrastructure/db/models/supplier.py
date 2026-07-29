"""Modelo ORM para la tabla proveedores."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.infrastructure.db.models.inventory_part import InventoryPartModel

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class SupplierModel(Base, TenantMixin, TimestampMixin, VersionMixin):
    """Modelo ORM para la tabla proveedores.

    Incluye VersionMixin para optimistic locking, TimestampMixin para
    created_at/updated_at, y TenantMixin para multi-tenancy por empresa_id.
    """

    __tablename__ = "proveedores"
    __table_args__ = (UniqueConstraint("empresa_id", "rif", name="uq_proveedores_empresa_rif"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    rif: Mapped[str | None] = mapped_column(String(20), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contacto: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    inventory_parts: Mapped[list[InventoryPartModel]] = relationship(
        "InventoryPartModel",
        back_populates="proveedor",
        cascade="save-update, merge",
    )
