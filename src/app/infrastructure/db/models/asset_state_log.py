"""Modelo ORM de SQLAlchemy para la tabla logs_estados_activos (AssetStateLog)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.db.models.asset import AssetModel

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import AssetStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class AssetStateLogModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de trazabilidad de cambios de estado de activos.

    Registra cada transición de estado de un activo físico, incluyendo
    estado anterior, nuevo estado, motivo, fecha del cambio y usuario responsable.
    """

    __tablename__ = "logs_estados_activos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    activo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("activos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    estado_anterior: Mapped[AssetStatus | None] = mapped_column(
        Enum(AssetStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
    )
    estado_nuevo: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_cambio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    asset: Mapped[AssetModel] = relationship(back_populates="state_logs")
