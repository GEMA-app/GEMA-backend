"""Schemas JSON:API para la API v1.

Re-exporta todos los schemas de los módulos para facilitar las importaciones.
"""

from app.presentation.api.v1.schemas.intervenciones import (
    CreateIntervencionRequest,
    IntervencionDocument,
    IntervencionListDocument,
    IntervencionResource,
    UpdateIntervencionRequest,
)

__all__ = [
    "CreateIntervencionRequest",
    "IntervencionDocument",
    "IntervencionListDocument",
    "IntervencionResource",
    "UpdateIntervencionRequest",
]