"""Modelos ORM para el módulo de órdenes de trabajo.

Define las tres tablas:
- ordenes_trabajo: tabla principal de órdenes de trabajo
- tecnicos_ordenes_trabajo: relación muchos a muchos con técnicos
- logs_estados_ordenes_trabajo: auditoría de cambios de estado
"""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.db.models.asset import AssetModel
    from app.infrastructure.db.models.technical_intervention import TechnicalInterventionModel

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import MaintenanceType, WorkOrderStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin


class WorkOrderModel(VersionMixin, TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla ordenes_trabajo.

    Almacena los datos persistentes de cada orden de trabajo,
    incluyendo su estado actual, costos y relaciones con activos y usuarios.
    """

    __tablename__ = "ordenes_trabajo"
    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo_ot", name="uq_ordenes_trabajo_empresa_codigo_ot"),
        Index("ix_ordenes_trabajo_empresa_activo", "empresa_id", "activo_id"),
        Index("ix_ordenes_trabajo_empresa_estado", "empresa_id", "estado"),
    )


    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    codigo_ot: Mapped[str] = mapped_column(String(30), nullable=False)
    activo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("activos.id", ondelete="RESTRICT"), nullable=False
    )
    reporte_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("reportes_fallas.id", ondelete="SET NULL"), nullable=True
    )
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("planes_mantenimiento.id", ondelete="SET NULL"), nullable=True
    )
    supervisor_id: Mapped[uuid.UUID | None] = mapped_column(

        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    tipo: Mapped[MaintenanceType] = mapped_column(
        Enum(MaintenanceType, name="tipo_mantenimiento",
             values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    estado: Mapped[WorkOrderStatus] = mapped_column(
        Enum(WorkOrderStatus, name="estado_orden_trabajo",
             values_callable=lambda obj: [e.value for e in obj]),
        default=WorkOrderStatus.OPEN,
        nullable=False,
    )
    fecha_apertura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_inicio_trabajo: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    descripcion_trabajo: Mapped[str | None] = mapped_column(Text, nullable=True)
    costo_estimado: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    costo_real: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    validado_por_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    fecha_validacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    activo: Mapped["AssetModel"] = relationship("AssetModel")
    intervenciones: Mapped[list["TechnicalInterventionModel"]] = relationship(
        "TechnicalInterventionModel",
        back_populates="orden_trabajo",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Representación legible de la instancia."""
        return f"<WorkOrder {self.codigo_ot}>"


class WorkOrderTechnicianModel(TenantMixin, Base):
    """Modelo ORM para la tabla tecnicos_ordenes_trabajo (relación N:M)."""

    __tablename__ = "tecnicos_ordenes_trabajo"

    ordenes_trabajo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ordenes_trabajo.id", ondelete="CASCADE"), primary_key=True
    )
    tecnico_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class WorkOrderStatusLogModel(TenantMixin, Base):
    """Modelo ORM para la tabla logs_estados_ordenes_trabajo (auditoría de estados)."""

    __tablename__ = "logs_estados_ordenes_trabajo"
    __table_args__ = (
        Index("ix_logs_estados_ot_empresa_ot", "empresa_id", "ordenes_trabajo_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ordenes_trabajo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ordenes_trabajo.id", ondelete="CASCADE"), nullable=False
    )
    estado_anterior: Mapped[WorkOrderStatus | None] = mapped_column(
        Enum(WorkOrderStatus, name="estado_orden_trabajo",
             values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
    )
    estado_nuevo: Mapped[WorkOrderStatus] = mapped_column(
        Enum(WorkOrderStatus, name="estado_orden_trabajo",
             values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_cambio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


