from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResourceIdentifier(BaseModel):
    """Identificador de recurso estándar de JSON:API."""

    type: str = Field(..., description="Tipo de recurso")
    id: str = Field(..., description="ID único del recurso")


class LinksObject(BaseModel):
    """Objeto de enlaces de JSON:API."""

    self: str | None = Field(None, description="Enlace al recurso actual")
    related: str | None = Field(None, description="Enlace al recurso relacionado")


class RelationshipObject(BaseModel):
    """Objeto de relación de JSON:API."""

    links: LinksObject | None = None
    data: ResourceIdentifier | list[ResourceIdentifier] | None = None
    meta: dict[str, Any] | None = None


class ErrorSource(BaseModel):
    """Origen de un error en JSON:API."""

    pointer: str | None = Field(None, description="Puntero JSON Pointer al atributo del error")
    parameter: str | None = Field(None, description="Nombre del parámetro de consulta o URL")


class ErrorObject(BaseModel):
    """Objeto de error estándar de JSON:API."""

    id: str | None = Field(None, description="Identificador único para esta ocurrencia del error")
    links: LinksObject | None = None
    status: str | None = Field(None, description="Código de estado HTTP aplicable a este problema")
    code: str | None = Field(None, description="Código de error interno de la aplicación")
    title: str | None = Field(None, description="Resumen corto y legible por humanos del problema")
    detail: str | None = Field(None, description="Explicación detallada del problema")
    source: ErrorSource | None = None
    meta: dict[str, Any] | None = None


class MetaObject(BaseModel):
    """Objeto de metadatos genérico de JSON:API."""

    model_config = ConfigDict(extra="allow")


class JsonApiErrorDocument(BaseModel):
    """Documento de error estándar de JSON:API."""

    errors: list[ErrorObject] = Field(..., description="Lista de errores ocurridos")
    meta: dict[str, Any] | None = None
