"""Modelo ORM de SQLAlchemy para la tabla de reportes de falla."""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import PriorityLevel, ReportStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class FailureReportModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de reportes de falla."""

    __tablename__ = "reportes_fallas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[PriorityLevel] = mapped_column(
        Enum(
            PriorityLevel,
            name="prioridad_nivel",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=PriorityLevel.MEDIUM,
        nullable=False,
    )
    reported_by: Mapped[str] = mapped_column(String(255), nullable=False)
    activo_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("activos.id", ondelete="RESTRICT"), nullable=True
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(
            ReportStatus, name="estado_reporte", values_callable=lambda obj: [e.value for e in obj]
        ),
        default=ReportStatus.PENDING,
        nullable=False,
    )
