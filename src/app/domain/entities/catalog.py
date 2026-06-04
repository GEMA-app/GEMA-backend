from dataclasses import dataclass
import uuid
from typing import Optional


@dataclass
class ArticleCategory:
    """Entidad de dominio placeholder para categorías de artículos."""
    id: uuid.UUID
    empresa_id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None


@dataclass
class CatalogArticle:
    """Entidad de dominio placeholder para artículos del catálogo."""
    id: uuid.UUID
    empresa_id: uuid.UUID
    categoria_id: Optional[uuid.UUID]
    nombre: str
    descripcion: Optional[str] = None
    fabricante: Optional[str] = None
    modelo: Optional[str] = None
    unidad_medida: Optional[str] = None
