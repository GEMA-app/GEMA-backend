# src/app/infrastructure/db/models/repuesto_utilizado.py
from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base


class RepuestoUtilizadoModel(Base):
    __tablename__ = "repuestos_utilizados"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    empresa_id: Mapped[UUID] = mapped_column(nullable=False)
    intervencion_id: Mapped[UUID] = mapped_column(
        ForeignKey("intervenciones_tecnicas.id", ondelete="CASCADE"), nullable=False
    )
    repuesto_id: Mapped[UUID] = mapped_column(
        ForeignKey("repuestos.id", ondelete="RESTRICT"), nullable=False
    )
    cantidad_usada: Mapped[int] = mapped_column(nullable=False)
    precio_unitario: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    moneda: Mapped[str] = mapped_column(String(3), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())