"""Enrutador principal de la API v1. Agrega todos los submÃ³dulos
de endpoints bajo el prefijo /v1.
"""

from fastapi import APIRouter

from app.presentation.api.v1.endpoints.assets import router as assets_router
from app.presentation.api.v1.endpoints.auth import router as auth_router
from app.presentation.api.v1.endpoints.companies import router as companies_router
from app.presentation.api.v1.endpoints.interventions import router as interventions_router
from app.presentation.api.v1.endpoints.locations import router as locations_router
from app.presentation.api.v1.endpoints.preferences import router as preferences_router
from app.presentation.api.v1.endpoints.roles import router as roles_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

v1_router.include_router(
    companies_router,
    prefix="/empresas",
    tags=["empresas"]
)

v1_router.include_router(
    roles_router,
    prefix="/empresas/{empresa_id}/roles",
    tags=["roles"]
)

v1_router.include_router(
    assets_router,
    prefix="/empresas/{empresa_id}/activos",
    tags=["activos"]
)

v1_router.include_router(
    locations_router,
    prefix="/empresas/{empresa_id}/ubicaciones",
    tags=["ubicaciones"]
)

v1_router.include_router(
    preferences_router,
    prefix="/empresas/{empresa_id}/yo/preferencias",
    tags=["preferencias"],
)

v1_router.include_router(
    interventions_router,
    tags=["intervenciones"],
)
