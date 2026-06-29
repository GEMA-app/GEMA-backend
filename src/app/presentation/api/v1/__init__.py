"""Módulo de la API v1.

Contiene todos los endpoints, schemas y dependencias de la versión 1
de la API REST del sistema GEMA.
"""

from app.presentation.api.v1.router import v1_router

__all__ = [
    "v1_router",
]
