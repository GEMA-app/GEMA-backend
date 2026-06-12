"""Schemas JSON:API para empresas: atributos, recursos,
documentos de empresa individual y listado.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import CompanyStatus
from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class CompanyAttributes(BaseModel):
    """Atributos de una empresa."""

    nombre: str
    slug: str
    estado: CompanyStatus
    rif: str | None = None
    email_contacto: str | None = None
    plan_id: str | None = None
    trial_hasta: str | None = None
    version: int


class CompanyResource(BaseModel):
    """Recurso JSON:API de una empresa."""

    type: str = Field(default="companies", description="Tipo de recurso")
    id: str = Field(..., description="ID único de la empresa")
    attributes: CompanyAttributes
    links: LinksObject | None = None


class CompanyDocument(BaseModel):
    """Documento JSON:API con una empresa."""

    data: CompanyResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class CompanyListDocument(BaseModel):
    """Documento JSON:API con lista de empresas."""

    data: list[CompanyResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateCompanyAttributes(BaseModel):
    """Atributos para crear una empresa."""

    nombre: str
    slug: str | None = None
    rif: str | None = None
    email_contacto: str | None = None


class CreateCompanyResource(BaseModel):
    """Recurso JSON:API para crear una empresa."""

    type: str = Field(default="companies", description="Tipo de recurso")
    attributes: CreateCompanyAttributes


class CreateCompanyRequest(BaseModel):
    """Solicitud JSON:API para crear una empresa."""

    data: CreateCompanyResource


class UpdateCompanyAttributes(BaseModel):
    """Atributos para actualizar una empresa."""

    nombre: str | None = None
    rif: str | None = None
    email_contacto: str | None = None
    estado: CompanyStatus | None = None
    version: int | None = None


class UpdateCompanyResource(BaseModel):
    """Recurso JSON:API para actualizar una empresa."""

    type: str = Field(default="companies", description="Tipo de recurso")
    attributes: UpdateCompanyAttributes


class UpdateCompanyRequest(BaseModel):
    """Solicitud JSON:API para actualizar una empresa."""

    data: UpdateCompanyResource
