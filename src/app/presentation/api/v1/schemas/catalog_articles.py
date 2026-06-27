"""Schemas JSON:API para artículos de catálogo."""

from typing import Any

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class CatalogArticleAttributes(BaseModel):
    """Atributos de un artículo de catálogo."""

    empresa_id: str
    category_id: str | None = None
    name: str
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_of_measure: str | None = None


class CatalogArticleResource(BaseModel):
    """Recurso JSON:API de un artículo de catálogo."""

    type: str = Field(default="catalog-articles", description="Tipo de recurso")
    id: str = Field(..., description="ID único del artículo")
    attributes: CatalogArticleAttributes
    links: LinksObject | None = None


class CatalogArticleDocument(BaseModel):
    """Documento JSON:API con un artículo de catálogo."""

    data: CatalogArticleResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class CatalogArticleListDocument(BaseModel):
    """Documento JSON:API con lista de artículos de catálogo."""

    data: list[CatalogArticleResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateCatalogArticleAttributes(BaseModel):
    """Atributos para crear un artículo de catálogo."""

    category_id: str | None = None
    name: str = Field(..., min_length=1)
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_of_measure: str | None = None


class CreateCatalogArticleResource(BaseModel):
    """Recurso JSON:API para crear un artículo de catálogo."""

    type: str = Field(default="catalog-articles", description="Tipo de recurso")
    attributes: CreateCatalogArticleAttributes


class CreateCatalogArticleRequest(BaseModel):
    """Solicitud JSON:API para crear un artículo de catálogo."""

    data: CreateCatalogArticleResource


class UpdateCatalogArticleAttributes(BaseModel):
    """Atributos para actualizar un artículo de catálogo."""

    category_id: str | None = None
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_of_measure: str | None = None


class UpdateCatalogArticleResource(BaseModel):
    """Recurso JSON:API para actualizar un artículo de catálogo."""

    type: str = Field(default="catalog-articles", description="Tipo de recurso")
    attributes: UpdateCatalogArticleAttributes


class UpdateCatalogArticleRequest(BaseModel):
    """Solicitud JSON:API para actualizar un artículo de catálogo."""

    data: UpdateCatalogArticleResource
