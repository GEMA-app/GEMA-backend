"""Entidad placeholder CatalogArticle (Artículo del Catálogo)."""

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CatalogArticle:
    """Entidad de dominio placeholder para artículos del catálogo.

    Diferido: Sprint futuro — Pendiente de implementación de comportamiento de dominio.
    """

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
