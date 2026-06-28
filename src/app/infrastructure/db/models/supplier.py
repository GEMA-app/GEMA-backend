"""Modelo ORM de SQLAlchemy para la tabla de proveedores."""

import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class SupplierModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de proveedores (`proveedores`)."""

    __tablename__ = "proveedores"
    __table_args__ = (
        UniqueConstraint("empresa_id", "rif", name="uq_proveedores_empresa_rif"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    rif: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contacto: Mapped[str | None] = mapped_column(String(255), nullable=True)
