"""Modelo ORM de SQLAlchemy para la tabla de reportes de falla."""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import PriorityLevel, ReportStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class FailureReportModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de reportes de falla."""

    __tablename__ = "failure_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[PriorityLevel] = mapped_column(
        Enum(PriorityLevel, values_callable=lambda obj: [e.value for e in obj]),
        default=PriorityLevel.MEDIUM,
        nullable=False,
    )
    reported_by: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=ReportStatus.PENDING,
        nullable=False,
    )
