"""Modelo ORM de SQLAlchemy para la tabla de planes de mantenimiento."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import MaintenanceType
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class MaintenancePlanModel(TenantMixin, VersionMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla ``planes_mantenimiento``."""

    __tablename__ = "planes_mantenimiento"
    __table_args__ = (
        Index("ix_planes_mantenimiento_empresa_id", "empresa_id"),
        Index("ix_planes_mantenimiento_empresa_activo", "empresa_id", "activo_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    activo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("activos.id", ondelete="RESTRICT"), nullable=False
    )
    tecnico_responsable_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[MaintenanceType] = mapped_column(
        Enum(MaintenanceType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    intervalo_dias: Mapped[int] = mapped_column(Integer, nullable=False)
    proxima_ejecucion: Mapped[date] = mapped_column(Date, nullable=False)
    descripcion_tareas: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
