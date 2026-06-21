from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.asset import AssetModel

class AssetStateLogModel(Base):
    __tablename__ = "logs_estados_activos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    activo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    estado_anterior: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String, nullable=False)
    fecha_cambio: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relación con el modelo de activos
    asset: Mapped[AssetModel] = relationship(back_populates="state_logs")