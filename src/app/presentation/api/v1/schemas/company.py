from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import CompanyStatus
from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class CompanyAttributes(BaseModel):
    nombre: str
    slug: str
    estado: CompanyStatus
    rif: str | None = None
    email_contacto: str | None = None
    plan_id: str | None = None
    trial_hasta: str | None = None
    version: int


class CompanyResource(BaseModel):
    type: str = Field(default="companies", description="Tipo de recurso")
    id: str = Field(..., description="ID único de la empresa")
    attributes: CompanyAttributes
    links: LinksObject | None = None


class CompanyDocument(BaseModel):
    data: CompanyResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class CompanyListDocument(BaseModel):
    data: list[CompanyResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateCompanyAttributes(BaseModel):
    nombre: str
    slug: str | None = None
    rif: str | None = None
    email_contacto: str | None = None


class CreateCompanyResource(BaseModel):
    type: str = Field(default="companies", description="Tipo de recurso")
    attributes: CreateCompanyAttributes


class CreateCompanyRequest(BaseModel):
    data: CreateCompanyResource


class UpdateCompanyAttributes(BaseModel):
    nombre: str | None = None
    rif: str | None = None
    email_contacto: str | None = None
    estado: CompanyStatus | None = None
    version: int | None = None


class UpdateCompanyResource(BaseModel):
    type: str = Field(default="companies", description="Tipo de recurso")
    attributes: UpdateCompanyAttributes


class UpdateCompanyRequest(BaseModel):
    data: UpdateCompanyResource
