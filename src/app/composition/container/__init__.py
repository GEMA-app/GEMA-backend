"""Paquete de composición de dependencias (Dependency Injection Container).

Re-exporta todas las fábricas públicas para mantener compatibilidad con los
imports existentes (``from app.composition.container import X``).
"""

from app.composition.container.asset import (
    get_asset_use_case,
    get_create_asset_use_case,
    get_delete_asset_use_case,
    get_list_assets_use_case,
    get_update_asset_use_case,
)
from app.composition.container.auth import (
    get_change_password_use_case,
    get_current_user_use_case,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_refresh_token_use_case,
    get_register_user_use_case,
    get_request_password_reset_use_case,
    get_reset_password_use_case,
)
from app.composition.container.common import (
    get_authorization_service,
    get_db_engine,
    get_notification_sender,
    get_password_hasher,
    get_redis_client,
    get_token_service,
    get_uow,
)
from app.composition.container.company import (
    get_company_use_case,
    get_create_company_use_case,
    get_delete_company_use_case,
    get_list_companies_use_case,
    get_update_company_use_case,
)
from app.composition.container.failure_report import (
    get_create_failure_report_use_case,
    get_delete_failure_report_use_case,
    get_failure_report_use_case,
    get_list_failure_reports_use_case,
    get_update_failure_report_use_case,
)
from app.composition.container.location import (
    get_create_location_use_case,
    get_delete_location_use_case,
    get_location_children_use_case,
    get_location_tree_use_case,
    get_location_use_case,
    get_update_location_use_case,
)
from app.composition.container.preference import (
    get_update_preference_use_case,
    get_user_preference_use_case,
)
from app.composition.container.role import (
    get_assign_role_to_user_use_case,
    get_create_role_use_case,
    get_delete_role_use_case,
    get_list_roles_use_case,
    get_revoke_role_from_user_use_case,
    get_role_use_case,
    get_update_role_use_case,
)
from app.composition.container.work_order import (
    get_change_work_order_status_use_case,
    get_create_work_order_use_case,
    get_delete_work_order_use_case,
    get_list_work_orders_use_case,
    get_update_work_order_use_case,
    get_work_order_use_case,
)

__all__ = [
    # Common
    "get_uow",
    "get_password_hasher",
    "get_token_service",
    "get_authorization_service",
    "get_notification_sender",
    "get_db_engine",
    "get_redis_client",
    # Auth
    "get_register_user_use_case",
    "get_login_user_use_case",
    "get_refresh_token_use_case",
    "get_logout_user_use_case",
    "get_current_user_use_case",
    "get_change_password_use_case",
    "get_request_password_reset_use_case",
    "get_reset_password_use_case",
    # Company
    "get_create_company_use_case",
    "get_company_use_case",
    "get_list_companies_use_case",
    "get_update_company_use_case",
    "get_delete_company_use_case",
    # Role
    "get_create_role_use_case",
    "get_role_use_case",
    "get_list_roles_use_case",
    "get_update_role_use_case",
    "get_delete_role_use_case",
    "get_assign_role_to_user_use_case",
    "get_revoke_role_from_user_use_case",
    # Asset
    "get_create_asset_use_case",
    "get_asset_use_case",
    "get_list_assets_use_case",
    "get_update_asset_use_case",
    "get_delete_asset_use_case",
    # Location
    "get_create_location_use_case",
    "get_location_use_case",
    "get_location_tree_use_case",
    "get_location_children_use_case",
    "get_update_location_use_case",
    "get_delete_location_use_case",
    # Preferences
    "get_update_preference_use_case",
    "get_user_preference_use_case",
    # FailureReport
    "get_create_failure_report_use_case",
    "get_failure_report_use_case",
    "get_list_failure_reports_use_case",
    "get_update_failure_report_use_case",
    "get_delete_failure_report_use_case",
    # Work Orders
    "get_create_work_order_use_case",
    "get_work_order_use_case",
    "get_list_work_orders_use_case",
    "get_update_work_order_use_case",
    "get_delete_work_order_use_case",
    "get_change_work_order_status_use_case",
]
