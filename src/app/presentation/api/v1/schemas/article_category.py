from pydantic import BaseModel, Field
from typing import Any

class ArticleCategoryAttributes(BaseModel):
    empresa_id: str
    nombre: str
    descripcion: str | None
    version: int

class ArticleCategoryResource(BaseModel):
    type: str = Field(default="article_categories")
    id: str
    attributes: ArticleCategoryAttributes

class ArticleCategoryDocument(BaseModel):
    data: ArticleCategoryResource
    meta: dict[str, Any] | None = None

class ArticleCategoryListDocument(BaseModel):
    data: list[ArticleCategoryResource]
    meta: dict[str, Any] | None = None