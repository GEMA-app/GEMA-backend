"""Modelo ORM de SQLAlchemy para la tabla de auditorías de sistema."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class SystemAudit(TimestampMixin, TenantMixin, Base):
    """Modelo ORM para la tabla de auditorías de sistema."""

    __tablename__ = "system_audits"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)
    accion = Column(String(255), nullable=False)
    detalles = Column(JSON, nullable=False)
    ip_address = Column(String(45), nullable=True)