"""Modelos ORM de SQLAlchemy para empresas y planes de suscripción."""

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import CompanyStatus
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.mixins import TimestampMixin, VersionMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.plan_execution import PlanExecutionModel
    from app.infrastructure.db.models.subscription_plan import SubscriptionPlanModel


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
        Enum(
            CompanyStatus, name="estado_empresa", values_callable=lambda obj: [e.value for e in obj]
        ),
        default=CompanyStatus.ACTIVE,
        nullable=False,
    )
    trial_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    plan: Mapped["SubscriptionPlanModel | None"] = relationship(
        "SubscriptionPlanModel", back_populates="empresas"
    )
    plan_executions: Mapped[list["PlanExecutionModel"]] = relationship(
        "PlanExecutionModel", back_populates="empresa"
    )
