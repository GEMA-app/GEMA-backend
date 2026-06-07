import uuid
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreateCompanyRequest:
    nombre: str
    slug: str | None = None
    rif: str | None = None
    email_contacto: str | None = None
    plan_id: uuid.UUID | None = None
    trial_hasta: date | None = None


@dataclass(frozen=True)
class UpdateCompanyRequest:
    nombre: str | None = None
    rif: str | None = None
    email_contacto: str | None = None
    estado: str | None = None


@dataclass(frozen=True)
class CompanyResponse:
    id: str
    nombre: str
    slug: str
    rif: str | None
    email_contacto: str | None
    estado: str
    plan_id: str | None
    trial_hasta: str | None
