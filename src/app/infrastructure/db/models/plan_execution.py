"""Modelo ORM para ejecuciones de planes de mantenimiento."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TimestampMixin


class PlanExecutionModel(Base, TimestampMixin):
    """Modelo ORM de ejecuciones de planes de mantenimiento."""

    __tablename__ = "planes_ejecuciones"
    __table_args__ = (
        Index("ix_planes_ejecuciones_empresa_plan", "empresa_id", "plan_id"),
        Index("ix_planes_ejecuciones_empresa_ot", "empresa_id", "ordenes_trabajo_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planes_mantenimiento.id", ondelete="CASCADE"),
        nullable=False,
    )
    work_order_id: Mapped[uuid.UUID] = mapped_column(
        "ordenes_trabajo_id",
        UUID(as_uuid=True),
        ForeignKey("ordenes_trabajo.id", ondelete="CASCADE"),
        nullable=False,
    )

    execution_date: Mapped[datetime] = mapped_column(
        "fecha_ejecucion", DateTime(timezone=True), nullable=False
    )
    observations: Mapped[str | None] = mapped_column(
        "observaciones", Text, nullable=True
    )

    empresa = relationship("CompanyModel", back_populates="plan_executions")
    # ponytail: FK a MaintenancePlanModel y WorkOrderModel en ramas separadas.
    # Se añadirán cuando esas ramas se fusionen a develop.

    def __repr__(self) -> str:
        """Representación legible del modelo."""
        return f"<PlanExecutionModel id={self.id} plan_id={self.plan_id}>"

