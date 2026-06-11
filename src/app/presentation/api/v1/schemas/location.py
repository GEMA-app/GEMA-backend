from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import LocationType
from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class LocationAttributes(BaseModel):
    empresa_id: str
    nombre: str
    tipo: LocationType
    parent_id: str | None = None
    descripcion: str | None = None


class LocationResource(BaseModel):
    type: str = Field(default="locations", description="Tipo de recurso")
    id: str = Field(..., description="ID único de la ubicación")
    attributes: LocationAttributes
    links: LinksObject | None = None


class LocationDocument(BaseModel):
    data: LocationResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class LocationListDocument(BaseModel):
    data: list[LocationResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Representación del Árbol (Tree)
class LocationTreeAttributes(BaseModel):
    nombre: str
    tipo: LocationType
    descripcion: str | None = None
    children: list[Any] = []  # Lista de LocationTreeResource


class LocationTreeResource(BaseModel):
    type: str = Field(default="locations", description="Tipo de recurso")
    id: str = Field(..., description="ID único de la ubicación")
    attributes: LocationTreeAttributes


class LocationTreeDocument(BaseModel):
    data: list[LocationTreeResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateLocationAttributes(BaseModel):
    nombre: str
    tipo: LocationType
    parent_id: str | None = None
    descripcion: str | None = None


class CreateLocationResource(BaseModel):
    type: str = Field(default="locations", description="Tipo de recurso")
    attributes: CreateLocationAttributes


class CreateLocationRequest(BaseModel):
    data: CreateLocationResource


class UpdateLocationAttributes(BaseModel):
    nombre: str | None = None
    tipo: LocationType | None = None
    parent_id: str | None = None
    descripcion: str | None = None


class UpdateLocationResource(BaseModel):
    type: str = Field(default="locations", description="Tipo de recurso")
    attributes: UpdateLocationAttributes


class UpdateLocationRequest(BaseModel):
    data: UpdateLocationResource
