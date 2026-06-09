"""Tests para seguridad de endpoints de roles."""
import inspect

from app.presentation.api.v1.endpoints.dependencies import (
    require_tenant_read,
)
from app.presentation.api.v1.endpoints.roles import (
    assign_role,
    get_role,
    list_roles,
    update_role,
)


def _get_dependency(func, param_name):
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_list_roles_uses_require_tenant_read():
    dep = _get_dependency(list_roles, "current_user")
    assert dep is require_tenant_read


def test_get_role_uses_require_tenant_read():
    dep = _get_dependency(get_role, "current_user")
    assert dep is require_tenant_read


def test_get_role_uses_role_id_param():
    sig = inspect.signature(get_role)
    assert "role_id" in sig.parameters


def test_update_role_uses_role_id_param():
    sig = inspect.signature(update_role)
    assert "role_id" in sig.parameters


def test_assign_role_uses_role_id_param():
    sig = inspect.signature(assign_role)
    assert "role_id" in sig.parameters
