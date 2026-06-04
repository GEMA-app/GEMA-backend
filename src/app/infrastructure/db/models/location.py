import uuid
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import LocationType
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin


class LocationModel(TenantMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de ubicaciones jerárquicas."""

    __tablename__ = "ubicaciones"
    __table_args__ = (Index("idx_ubicaciones_empresa_parent", "empresa_id", "parent_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ubicaciones.id", ondelete="CASCADE"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[LocationType] = mapped_column(
        Enum(LocationType, values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relación jerárquica auto-referencial
    parent: Mapped[Optional["LocationModel"]] = relationship(
        "LocationModel", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["LocationModel"]] = relationship(
        "LocationModel", back_populates="parent", cascade="all, delete-orphan"
    )
