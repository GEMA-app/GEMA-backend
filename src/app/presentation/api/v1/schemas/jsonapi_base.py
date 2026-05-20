from typing import Any, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class ResourceIdentifier(BaseModel):
    """Identificador de recurso estándar de JSON:API."""

    type: str = Field(..., description="Tipo de recurso")
    id: str = Field(..., description="ID único del recurso")


class LinksObject(BaseModel):
    """Objeto de enlaces de JSON:API."""

    self: Optional[str] = Field(None, description="Enlace al recurso actual")
    related: Optional[str] = Field(None, description="Enlace al recurso relacionado")


class RelationshipObject(BaseModel):
    """Objeto de relación de JSON:API."""

    links: Optional[LinksObject] = None
    data: Optional[Union[ResourceIdentifier, list[ResourceIdentifier]]] = None
    meta: Optional[dict[str, Any]] = None


class ErrorSource(BaseModel):
    """Origen de un error en JSON:API."""

    pointer: Optional[str] = Field(None, description="Puntero JSON Pointer al atributo del error")
    parameter: Optional[str] = Field(None, description="Nombre del parámetro de consulta o URL")


class ErrorObject(BaseModel):
    """Objeto de error estándar de JSON:API."""

    id: Optional[str] = Field(None, description="Identificador único para esta ocurrencia del error")
    links: Optional[LinksObject] = None
    status: Optional[str] = Field(None, description="Código de estado HTTP aplicable a este problema")
    code: Optional[str] = Field(None, description="Código de error interno de la aplicación")
    title: Optional[str] = Field(None, description="Resumen corto y legible por humanos del problema")
    detail: Optional[str] = Field(None, description="Explicación detallada del problema")
    source: Optional[ErrorSource] = None
    meta: Optional[dict[str, Any]] = None


class MetaObject(BaseModel):
    """Objeto de metadatos genérico de JSON:API."""

    model_config = ConfigDict(extra="allow")


class JsonApiErrorDocument(BaseModel):
    """Documento de error estándar de JSON:API."""

    errors: list[ErrorObject] = Field(..., description="Lista de errores ocurridos")
    meta: Optional[dict[str, Any]] = None
