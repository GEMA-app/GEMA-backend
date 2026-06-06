import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.enums import CompanyStatus
from app.domain.events import CompanyCreated, DomainEvent
from app.domain.exceptions import EmptyCompanyNameError
from app.domain.value_objects import CompanyId, Slug


@dataclass
class Company:
    """Entidad que representa una Empresa (Tenant) en la plataforma GEMA."""

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
        """Método fábrica para crear una nueva empresa y emitir CompanyCreated."""
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
