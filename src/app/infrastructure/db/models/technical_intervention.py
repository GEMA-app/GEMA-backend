"""Modelo ORM de SQLAlchemy para la tabla de intervenciones técnicas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.user import UserModel
    from app.infrastructure.db.models.work_order import WorkOrderModel


class TechnicalInterventionModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de intervenciones técnicas (`intervenciones_tecnicas`)."""

    __tablename__ = "intervenciones_tecnicas"
    __table_args__ = (
        Index("ix_intervenciones_tecnicas_empresa_ot", "empresa_id", "ordenes_trabajo_id"),
        Index("ix_intervenciones_tecnicas_empresa_tecnico", "empresa_id", "tecnico_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ordenes_trabajo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ordenes_trabajo.id", ondelete="CASCADE"), nullable=False
    )
    tecnico_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    fecha_inicio: Mapped[datetime] = mapped_column(nullable=False)
    fecha_fin: Mapped[datetime | None] = mapped_column(nullable=True)
    horas_hombre: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    tareas_realizadas: Mapped[str] = mapped_column(nullable=False)

    # Relaciones
    orden_trabajo: Mapped["WorkOrderModel"] = relationship(
        "WorkOrderModel", back_populates="intervenciones"
    )
    tecnico: Mapped["UserModel"] = relationship("UserModel")
