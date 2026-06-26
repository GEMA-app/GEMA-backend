"""Schemas JSON:API para ubicaciones jerárquicas: atributos,
recursos, documentos, árbol de ubicaciones y solicitudes.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import LocationType
from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class LocationAttributes(BaseModel):
    """Atributos de una ubicación."""

    empresa_id: str
    nombre: str
    tipo: LocationType
    parent_id: str | None = None
    descripcion: str | None = None
    version: int


class LocationResource(BaseModel):
    """Recurso JSON:API de una ubicación."""

    type: str = Field(default="locations", description="Tipo de recurso")
    id: str = Field(..., description="ID único de la ubicación")
    attributes: LocationAttributes
    links: LinksObject | None = None


class LocationDocument(BaseModel):
    """Documento JSON:API con una ubicación."""

    data: LocationResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class LocationListDocument(BaseModel):
    """Documento JSON:API con lista de ubicaciones."""

    data: list[LocationResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Representación del Árbol (Tree)
class LocationTreeAttributes(BaseModel):
    """Atributos de una ubicación en el árbol jerárquico."""

    nombre: str
    tipo: LocationType
    descripcion: str | None = None
    children: list["LocationTreeResource"] = Field(default_factory=list)


class LocationTreeResource(BaseModel):
    """Recurso JSON:API de una ubicación en el árbol."""

    type: str = Field(default="locations", description="Tipo de recurso")
    id: str = Field(..., description="ID único de la ubicación")
    attributes: LocationTreeAttributes


class LocationTreeDocument(BaseModel):
    """Documento JSON:API con el árbol de ubicaciones."""

    data: list[LocationTreeResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateLocationAttributes(BaseModel):
    """Atributos para crear una ubicación."""

    nombre: str
    tipo: LocationType
    parent_id: str | None = None
    descripcion: str | None = None


class CreateLocationResource(BaseModel):
    """Recurso JSON:API para crear una ubicación."""

    type: str = Field(default="locations", description="Tipo de recurso")
    attributes: CreateLocationAttributes


class CreateLocationRequest(BaseModel):
    """Solicitud JSON:API para crear una ubicación."""

    data: CreateLocationResource


class UpdateLocationAttributes(BaseModel):
    """Atributos para actualizar una ubicación."""

    nombre: str | None = None
    tipo: LocationType | None = None
    parent_id: str | None = None
    descripcion: str | None = None
    version: int | None = None


class UpdateLocationResource(BaseModel):
    """Recurso JSON:API para actualizar una ubicación."""

    type: str = Field(default="locations", description="Tipo de recurso")
    attributes: UpdateLocationAttributes


class UpdateLocationRequest(BaseModel):
    """Solicitud JSON:API para actualizar una ubicación."""

    data: UpdateLocationResource
