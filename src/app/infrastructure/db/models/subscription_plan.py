import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.company import CompanyModel


class SubscriptionPlanModel(Base, TimestampMixin):
    """Modelo ORM para la tabla de planes de suscripción (plataforma, sin tenant)."""
    __tablename__ = "planes_suscripcion"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_activos: Mapped[int | None] = mapped_column(nullable=True)
    max_usuarios: Mapped[int | None] = mapped_column(nullable=True)
    precio_mensual_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    empresas: Mapped[list["CompanyModel"]] = relationship(
        "CompanyModel", back_populates="plan"
    )
