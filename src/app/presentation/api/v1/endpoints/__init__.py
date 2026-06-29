"""Endpoints de la API v1.

Re-exporta todos los routers de los endpoints de la versión 1 de la API
para que puedan ser registrados en el router principal.
"""

from app.presentation.api.v1.endpoints.article_category import router as article_category_router
from app.presentation.api.v1.endpoints.asset_state_log import router as asset_state_log_router
from app.presentation.api.v1.endpoints.assets import router as assets_router
from app.presentation.api.v1.endpoints.auth import router as auth_router
from app.presentation.api.v1.endpoints.catalog_articles import router as catalog_articles_router
from app.presentation.api.v1.endpoints.companies import router as companies_router
from app.presentation.api.v1.endpoints.failure_reports import router as failure_reports_router
from app.presentation.api.v1.endpoints.interventions import router as interventions_router
from app.presentation.api.v1.endpoints.locations import router as locations_router
from app.presentation.api.v1.endpoints.maintenance_plan import router as maintenance_plan_router
from app.presentation.api.v1.endpoints.plan_executions import router as plan_executions_router
from app.presentation.api.v1.endpoints.preferences import router as preferences_router
from app.presentation.api.v1.endpoints.roles import router as roles_router
from app.presentation.api.v1.endpoints.subscription_plans import router as subscription_plans_router
from app.presentation.api.v1.endpoints.system_audit import router as system_audit_router
from app.presentation.api.v1.endpoints.used_parts import router as used_parts_router
from app.presentation.api.v1.endpoints.users import router as users_router
from app.presentation.api.v1.endpoints.work_orders import router as work_orders_router

__all__ = [
    "article_category_router",
    "asset_state_log_router",
    "assets_router",
    "auth_router",
    "catalog_articles_router",
    "companies_router",
    "failure_reports_router",
    "interventions_router",
    "locations_router",
    "maintenance_plan_router",
    "plan_executions_router",
    "preferences_router",
    "roles_router",
    "subscription_plans_router",
    "system_audit_router",
    "used_parts_router",
    "users_router",
    "work_orders_router",
]
