"""Tests de seguridad para los endpoints de SubscriptionPlan."""
import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.dependencies import (
    get_current_active_user,
)
from app.presentation.api.v1.endpoints.subscription_plans import (
    create_subscription_plan,
    delete_subscription_plan,
    get_subscription_plan,
    list_subscription_plans,
    update_subscription_plan,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_list_plans_uses_get_current_active_user() -> None:
    dep = _get_dependency(list_subscription_plans, "current_user")
    assert dep is get_current_active_user


def test_get_plan_uses_get_current_active_user() -> None:
    dep = _get_dependency(get_subscription_plan, "current_user")
    assert dep is get_current_active_user


def test_get_plan_uses_plan_id_param() -> None:
    sig = inspect.signature(get_subscription_plan)
    assert "plan_id" in sig.parameters


def test_update_plan_uses_plan_id_param() -> None:
    sig = inspect.signature(update_subscription_plan)
    assert "plan_id" in sig.parameters


def test_delete_plan_uses_plan_id_param() -> None:
    sig = inspect.signature(delete_subscription_plan)
    assert "plan_id" in sig.parameters


def test_create_plan_uses_require_platform_permission() -> None:
    dep = _get_dependency(create_subscription_plan, "current_user")
    assert dep is not None
    assert callable(dep)
    # Verificar que valida los permisos de admin
    import inspect as _inspect
    source = _inspect.getsource(create_subscription_plan)
    assert "require_platform_permission(PermissionModule.ADMIN, \"create\")" in source


def test_update_plan_uses_require_platform_permission() -> None:
    dep = _get_dependency(update_subscription_plan, "current_user")
    assert dep is not None
    assert callable(dep)
    # Verificar que valida los permisos de admin
    import inspect as _inspect
    source = _inspect.getsource(update_subscription_plan)
    assert "require_platform_permission(PermissionModule.ADMIN, \"edit\")" in source


def test_delete_plan_uses_require_platform_permission() -> None:
    dep = _get_dependency(delete_subscription_plan, "current_user")
    assert dep is not None
    assert callable(dep)
    # Verificar que valida los permisos de admin
    import inspect as _inspect
    source = _inspect.getsource(delete_subscription_plan)
    assert "require_platform_permission(PermissionModule.ADMIN, \"delete\")" in source
