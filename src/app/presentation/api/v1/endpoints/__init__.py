"""Endpoints de la API v1.

Re-exporta todos los routers de los endpoints de la versión 1 de la API
para que puedan ser registrados en el router principal.
"""

from app.presentation.api.v1.endpoints.intervenciones import router as intervenciones_router

__all__ = [
    "intervenciones_router",
]