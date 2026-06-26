"""Modelos ORM de SQLAlchemy para empresas y planes de suscripción."""

import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import CompanyStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TimestampMixin, VersionMixin


class SubscriptionPlanModel(TimestampMixin, Base):
    """Modelo ORM para planes de suscripción de la plataforma."""

    __tablename__ = "planes_suscripcion"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_activos: Mapped[int | None] = mapped_column(nullable=True)
    max_usuarios: Mapped[int | None] = mapped_column(nullable=True)
    precio_mensual_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    empresas: Mapped[list["CompanyModel"]] = relationship("CompanyModel", back_populates="plan")


class CompanyModel(VersionMixin, TimestampMixin, Base):
    """Modelo ORM para la tabla de empresas (tenants)."""

    __tablename__ = "empresas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("planes_suscripcion.id", ondelete="SET NULL"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(63), unique=True, index=True, nullable=False)
    rif: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email_contacto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[CompanyStatus] = mapped_column(
        Enum(CompanyStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=CompanyStatus.ACTIVE,
        nullable=False,
    )
    trial_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    plan: Mapped[SubscriptionPlanModel | None] = relationship(
        "SubscriptionPlanModel", back_populates="empresas"
    )
