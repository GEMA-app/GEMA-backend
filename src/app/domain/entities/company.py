"""Entidad Company — empresa/tenant del sistema SaaS con su ciclo de vida y eventos de dominio."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.enums import CompanyStatus
from app.domain.events import (
    CompanyActivated,
    CompanyCancelled,
    CompanyCreated,
    CompanySuspended,
    DomainEvent,
    EventProducer,
)
from app.domain.exceptions import (
    CompanyAlreadyCancelledError,
    CompanyNotSuspendedError,
    EmptyCompanyNameError,
)
from app.domain.value_objects import CompanyId, Slug


@dataclass
class Company(EventProducer):
    """Entidad con comportamiento (Rich Entity) que representa una Empresa (Tenant) en GEMA."""

    id: CompanyId
    nombre: str
    slug: Slug
    rif: str | None = None
    email_contacto: str | None = None
    estado: CompanyStatus = CompanyStatus.ACTIVE
    plan_id: uuid.UUID | None = None
    trial_hasta: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        nombre: str,
        slug: Slug,
        rif: str | None = None,
        email_contacto: str | None = None,
        plan_id: uuid.UUID | None = None,
        trial_hasta: date | None = None,
        estado: CompanyStatus = CompanyStatus.ACTIVE,
    ) -> "Company":
        """Método fábrica para crear una nueva empresa y emitir CompanyCreated.

        Args:
            nombre: Nombre de la empresa (no puede estar vacío).
            slug: Slug URL-friendly identificador de la empresa.
            rif: Registro de Información Fiscal de la empresa (opcional).
            email_contacto: Correo electrónico de contacto (opcional).
            plan_id: Identificador del plan de suscripción (opcional).
            trial_hasta: Fecha hasta la cual aplica el período de prueba (opcional).
            estado: Estado inicial de la empresa. Por defecto ACTIVE.

        Returns:
            La nueva entidad Company creada con el evento CompanyCreated emitido.

        Raises:
            EmptyCompanyNameError: Si el nombre de la empresa está vacío.
        """
        if not nombre or not nombre.strip():
            raise EmptyCompanyNameError("El nombre de la empresa no puede estar vacío.")

        company_id = CompanyId(value=uuid.uuid4())
        company = cls(
            id=company_id,
            nombre=nombre.strip(),
            slug=slug,
            rif=rif,
            email_contacto=email_contacto,
            estado=estado,
            plan_id=plan_id,
            trial_hasta=trial_hasta,
        )
        company._events.append(
            CompanyCreated(
                company_id=str(company.id), nombre=company.nombre, slug=company.slug.value
            )
        )
        return company

    def pull_events(self) -> list[DomainEvent]:
        """Devuelve los eventos de dominio acumulados y limpia la lista interna."""
        events = self._events.copy()
        self._events.clear()
        return events

    def rename(self, new_name: str) -> None:
        """Cambia el nombre de la empresa y realiza validaciones."""
        stripped = new_name.strip()
        if not stripped:
            raise EmptyCompanyNameError("El nombre de la empresa no puede estar vacío.")
        self.nombre = stripped

    def update_profile(
        self,
        rif: str | None = None,
        email_contacto: str | None = None,
    ) -> None:
        """Actualiza los campos de perfil de la empresa."""
        self.rif = rif
        self.email_contacto = email_contacto

    def suspend(self) -> None:
        """Suspende la empresa. No se puede suspender si ya está cancelada."""
        if self.estado == CompanyStatus.CANCELLED:
            raise CompanyAlreadyCancelledError("No se puede suspender una empresa cancelada.")
        self.estado = CompanyStatus.SUSPENDED
        self._events.append(CompanySuspended(company_id=str(self.id)))

    def activate(self) -> None:
        """Reactiva una empresa suspendida."""
        if self.estado != CompanyStatus.SUSPENDED:
            raise CompanyNotSuspendedError("Solo se pueden reactivar empresas suspendidas.")
        self.estado = CompanyStatus.ACTIVE
        self._events.append(CompanyActivated(company_id=str(self.id)))

    def cancel(self) -> None:
        """Cancela la empresa definitivamente.

        Es idempotente: si la empresa ya está cancelada, es no-op.
        """
        if self.estado == CompanyStatus.CANCELLED:
            return  # no-op idempotente
        self.estado = CompanyStatus.CANCELLED
        self._events.append(CompanyCancelled(company_id=str(self.id)))
