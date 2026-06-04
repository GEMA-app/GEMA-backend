import uuid
from dataclasses import dataclass


@dataclass
class ArticleCategory:
    """Entidad de dominio placeholder para categorías de artículos."""

    id: uuid.UUID
    empresa_id: uuid.UUID
    nombre: str
    descripcion: str | None = None


@dataclass
class CatalogArticle:
    """Entidad de dominio placeholder para artículos del catálogo."""

    id: uuid.UUID
    empresa_id: uuid.UUID
    categoria_id: uuid.UUID | None
    nombre: str
    descripcion: str | None = None
    fabricante: str | None = None
    modelo: str | None = None
    unidad_medida: str | None = None
