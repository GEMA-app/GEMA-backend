import uuid
from datetime import date
from typing import Optional
from sqlalchemy import String, Text, Numeric, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TimestampMixin
from app.domain.enums import CompanyStatus


class SubscriptionPlanModel(TimestampMixin, Base):
    """Modelo ORM para planes de suscripción de la plataforma."""

    __tablename__ = "planes_suscripcion"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_activos: Mapped[Optional[int]] = mapped_column(nullable=True)
    max_usuarios: Mapped[Optional[int]] = mapped_column(nullable=True)
    precio_mensual_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relación con empresas
    empresas: Mapped[list["CompanyModel"]] = relationship("CompanyModel", back_populates="plan")


class CompanyModel(TimestampMixin, Base):
    """Modelo ORM para la tabla de empresas (tenants)."""

    __tablename__ = "empresas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("planes_suscripcion.id", ondelete="SET NULL"),
        nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(63), unique=True, index=True, nullable=False)
    rif: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email_contacto: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    estado: Mapped[CompanyStatus] = mapped_column(
        Enum(CompanyStatus),
        default=CompanyStatus.ACTIVE,
        nullable=False
    )
    trial_hasta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relación con el plan de suscripción
    plan: Mapped[Optional[SubscriptionPlanModel]] = relationship("SubscriptionPlanModel", back_populates="empresas")
