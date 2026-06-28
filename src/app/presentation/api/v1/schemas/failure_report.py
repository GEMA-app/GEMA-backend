"""Schemas JSON:API para reportes de falla: atributos, recursos
y documentos individuales.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class FailureReportAttributes(BaseModel):
    """Atributos de un reporte de falla en una respuesta JSON:API."""

    title: str
    description: str
    location: str
    priority: str
    reported_by: str
    status: str
    created_at: datetime


class FailureReportResource(BaseModel):
    """Recurso JSON:API que encapsula los atributos de un reporte de falla."""

    type: str = Field(default="failure-reports")
    id: str
    attributes: FailureReportAttributes
    links: LinksObject | None = None


class FailureReportDocument(BaseModel):
    """Documento JSON:API con un único recurso de reporte de falla."""

    data: FailureReportResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class FailureReportListDocument(BaseModel):
    """Documento JSON:API con una colección de reportes de falla."""

    data: list[FailureReportResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class CreateFailureReportAttributes(BaseModel):
    """Atributos de entrada para crear un nuevo reporte de falla."""

    title: str
    description: str
    location: str
    priority: str
    reported_by: str


class CreateFailureReportResource(BaseModel):
    """Recurso JSON:API de entrada para la creación de un reporte de falla."""

    type: str = Field(default="failure-reports")
    attributes: CreateFailureReportAttributes


class CreateFailureReportRequest(BaseModel):
    """Cuerpo completo de la solicitud POST para crear un reporte de falla."""

    data: CreateFailureReportResource


class UpdateFailureReportAttributes(BaseModel):
    """Atributos opcionales para la actualización parcial de un reporte de falla."""

    title: str | None = None
    description: str | None = None
    location: str | None = None
    priority: str | None = None
    reported_by: str | None = None
    status: str | None = None
    version: int | None = None


class UpdateFailureReportResource(BaseModel):
    """Recurso JSON:API de entrada para actualizar un reporte de falla."""

    type: str = Field(default="failure-reports")
    attributes: UpdateFailureReportAttributes


class UpdateFailureReportRequest(BaseModel):
    """Cuerpo completo de la solicitud PATCH para actualizar un reporte de falla."""

    data: UpdateFailureReportResource
