import uuid
from dataclasses import dataclass, field
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
    _fields_set: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self._fields_set:
            fields_with_values = {
                name for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))


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
