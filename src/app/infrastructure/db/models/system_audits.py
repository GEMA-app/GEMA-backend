"""Modelo ORM de SQLAlchemy para la tabla de auditorías de sistema."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class SystemAuditModel(TimestampMixin, TenantMixin, Base):
    """Modelo ORM para la tabla de auditorías de sistema (`auditorias_sistema`)."""

    __tablename__ = "auditorias_sistema"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, index=True)
    accion: Mapped[str] = mapped_column(String(255))
    detalles: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    ocurrido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
