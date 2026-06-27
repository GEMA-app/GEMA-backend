"""Schemas de solicitud y respuesta JSON:API para Categorías de Artículos del Catálogo."""

from typing import Any

from pydantic import BaseModel, Field


class ArticleCategoryAttributes(BaseModel):
    """Atributos de una categoría de artículo según JSON:API.

    Attributes:
        empresa_id: UUID de la empresa a la que pertenece.
        name: Nombre único de la categoría dentro del tenant.
        description: Descripción opcional de la categoría.
        version: Versión para control de concurrencia optimista.
    """

    empresa_id: str
    name: str
    description: str | None
    version: int


class ArticleCategoryResource(BaseModel):
    """Recurso JSON:API que envuelve los atributos de la categoría.

    Attributes:
        type: Tipo de recurso (article_categories).
        id: UUID de la categoría.
        attributes: Atributos específicos de la categoría.
    """

    type: str = Field(default="article_categories")
    id: str
    attributes: ArticleCategoryAttributes


class ArticleCategoryDocument(BaseModel):
    """Documento JSON:API con un único recurso de categoría.

    Attributes:
        data: Recurso de categoría.
        meta: Metadatos opcionales.
    """

    data: ArticleCategoryResource
    meta: dict[str, Any] | None = None


class ArticleCategoryListDocument(BaseModel):
    """Documento JSON:API con una lista de recursos de categoría.

    Attributes:
        data: Lista de recursos de categoría.
        meta: Metadatos opcionales.
    """

    data: list[ArticleCategoryResource]
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateCategoryAttributes(BaseModel):
    """Atributos para crear una categoría de artículo."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)


class CreateCategoryResource(BaseModel):
    """Recurso JSON:API para crear una categoría de artículo."""

    type: str = Field(default="article_categories", description="Tipo de recurso")
    attributes: CreateCategoryAttributes


class CreateCategoryRequest(BaseModel):
    """Solicitud JSON:API para crear una categoría de artículo."""

    data: CreateCategoryResource


class UpdateCategoryAttributes(BaseModel):
    """Atributos para actualizar una categoría de artículo."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    version: int | None = Field(None, description="Versión para locking optimista")


class UpdateCategoryResource(BaseModel):
    """Recurso JSON:API para actualizar una categoría de artículo."""

    type: str = Field(default="article_categories", description="Tipo de recurso")
    attributes: UpdateCategoryAttributes


class UpdateCategoryRequest(BaseModel):
    """Solicitud JSON:API para actualizar una categoría de artículo."""

    data: UpdateCategoryResource

