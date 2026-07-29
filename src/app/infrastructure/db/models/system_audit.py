"""Modelo ORM de SQLAlchemy para la tabla de auditorías de sistema."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.user import UserModel


class SystemAuditModel(TimestampMixin, TenantMixin, Base):
    """Modelo ORM para la tabla de auditorías de sistema (`auditorias_sistema`)."""

    __tablename__ = "auditorias_sistema"
    __table_args__ = (
        Index("ix_auditorias_sistema_empresa_usuario", "empresa_id", "usuario_id"),
        Index("ix_auditorias_sistema_empresa_ocurrido", "empresa_id", "ocurrido_en"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    accion: Mapped[str] = mapped_column(String(255))
    detalles: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    ocurrido_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    usuario: Mapped[UserModel | None] = relationship("UserModel", lazy="selectin")
