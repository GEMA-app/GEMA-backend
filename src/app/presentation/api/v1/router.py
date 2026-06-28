"""Enrutador principal de la API v1. Agrega todos los submódulos
de endpoints bajo el prefijo /v1.
"""

from fastapi import APIRouter

from app.presentation.api.v1.endpoints.article_category import router as article_category_router
from app.presentation.api.v1.endpoints.asset_state_log import router as asset_state_log_router
from app.presentation.api.v1.endpoints.assets import router as assets_router
from app.presentation.api.v1.endpoints.auth import router as auth_router
from app.presentation.api.v1.endpoints.catalog_articles import router as catalog_articles_router
from app.presentation.api.v1.endpoints.companies import router as companies_router
from app.presentation.api.v1.endpoints.failure_reports import router as failure_reports_router
from app.presentation.api.v1.endpoints.locations import router as locations_router
from app.presentation.api.v1.endpoints.maintenance_plan import router as maintenance_plan_router
from app.presentation.api.v1.endpoints.plan_executions import router as plan_executions_router
from app.presentation.api.v1.endpoints.preferences import router as preferences_router
from app.presentation.api.v1.endpoints.roles import router as roles_router
from app.presentation.api.v1.endpoints.subscription_plans import router as subscription_plans_router
from app.presentation.api.v1.endpoints.used_parts import router as used_parts_router
from app.presentation.api.v1.endpoints.work_orders import router as work_orders_router

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
    tags=["activos"],
)

v1_router.include_router(
    locations_router,
    prefix="/empresas/{empresa_id}/ubicaciones",
    tags=["ubicaciones"],
)

v1_router.include_router(
    preferences_router,
    prefix="/empresas/{empresa_id}/yo/preferencias",
    tags=["preferencias"],
)

v1_router.include_router(
    failure_reports_router,
    prefix="/empresas/{empresa_id}/reportes-fallas",
    tags=["Reporte de Fallas"],
)

v1_router.include_router(
    used_parts_router,
    prefix="/empresas/{empresa_id}/ordenes-trabajo/{ot_id}/intervenciones/{intervencion_id}/repuestos-utilizados",
    tags=["Repuestos Utilizados"],
)

v1_router.include_router(
    asset_state_log_router,
    prefix="/empresas/{empresa_id}/activos",
    tags=["Historial Estados Activos"],
)

v1_router.include_router(
    article_category_router,
    prefix="/empresas/{empresa_id}/catalogo/categorias",
    tags=["Categorías de Catálogo"],
)

v1_router.include_router(
    catalog_articles_router,
    prefix="/empresas/{empresa_id}/catalogo/articulos",
    tags=["catalogo"],
)

v1_router.include_router(
    work_orders_router,
    prefix="/empresas/{empresa_id}/ordenes-trabajo",
    tags=["ordenes-trabajo"],
)

v1_router.include_router(
    plan_executions_router,
    prefix="/empresas/{empresa_id}/planes-mantenimiento/{plan_id}/ejecuciones",
    tags=["ejecuciones-plan"],
)

v1_router.include_router(
    subscription_plans_router,
    prefix="/planes",
    tags=["planes"]
)

v1_router.include_router(
    maintenance_plan_router,
    prefix="/empresas/{empresa_id}/planes-mantenimiento",
    tags=["planes-mantenimiento"],
)
