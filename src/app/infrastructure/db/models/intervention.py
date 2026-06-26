"""Modelo ORM para intervenciones técnicas."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class InterventionModel(Base, TenantMixin, TimestampMixin):
    """Modelo ORM para la tabla intervenciones_tecnicas. Incluye TenantMixin y TimestampMixin."""

    __tablename__ = "intervenciones_tecnicas"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        index=True,
    )
    ordenes_trabajo_id: Mapped[UUID] = mapped_column(
        ForeignKey("ordenes_trabajo.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tecnico_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
    tareas_realizadas: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    horas_hombre: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
