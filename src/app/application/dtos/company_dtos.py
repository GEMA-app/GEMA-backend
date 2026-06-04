from dataclasses import dataclass
from datetime import date
from typing import Optional
import uuid


@dataclass(frozen=True)
class CreateCompanyRequest:
    nombre: str
    slug: Optional[str] = None
    rif: Optional[str] = None
    email_contacto: Optional[str] = None
    plan_id: Optional[uuid.UUID] = None
    trial_hasta: Optional[date] = None


@dataclass(frozen=True)
class UpdateCompanyRequest:
    nombre: Optional[str] = None
    rif: Optional[str] = None
    email_contacto: Optional[str] = None
    estado: Optional[str] = None


@dataclass(frozen=True)
class CompanyResponse:
    id: str
    nombre: str
    slug: str
    rif: Optional[str]
    email_contacto: Optional[str]
    estado: str
    plan_id: Optional[str]
    trial_hasta: Optional[str]
