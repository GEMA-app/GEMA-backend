import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleCategory:
    """Entidad de dominio placeholder para categorías de artículos."""

    id: uuid.UUID
    empresa_id: uuid.UUID
    nombre: str
    descripcion: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


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
    created_at: datetime | None = None
    updated_at: datetime | None = None
