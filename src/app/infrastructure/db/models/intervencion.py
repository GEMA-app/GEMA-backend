"""Modelo ORM para intervenciones técnicas."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import EstadoIntervencion
from app.infrastructure.db.models.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class IntervencionModel(Base, TenantMixin, TimestampMixin):
    """Modelo ORM para la tabla intervenciones_tecnicas."""

    __tablename__ = "intervenciones_tecnicas"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        index=True,
    )
    orden_trabajo_id: Mapped[UUID] = mapped_column(
        ForeignKey("ordenes_trabajo.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tecnico_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    horas_trabajadas: Mapped[float] = mapped_column(Float, nullable=False)
    costo: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[EstadoIntervencion] = mapped_column(String(20), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)