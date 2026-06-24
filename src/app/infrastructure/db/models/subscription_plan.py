import uuid
from decimal import Decimal

from sqlalchemy import  Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TimestampMixin, TenantMixin, VersionMixin

class SubscriptionPlanModel(Base, TimestampMixin, TenantMixin, VersionMixin):
    """Modelo ORM para la tabla de planes de suscripción."""
    __tablename__ = "planes_suscripcion"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_activos: Mapped[int | None] = mapped_column(nullable=True)
    max_usuarios: Mapped[int | None] = mapped_column(nullable=True)
    precio_mensual_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    # start_date: Mapped[datetime] = mapped_column(nullable=False)
    # end_date: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)