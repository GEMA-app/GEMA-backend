"""Tests para seguridad de endpoints de ubicaciones."""
import inspect

from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
    require_tenant_read,
)
from app.presentation.api.v1.endpoints.locations import (
    create_location,
    delete_location,
    get_location,
    get_location_children,
    get_location_tree,
    update_location,
)


def _get_dependency(func, param_name):
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_get_location_tree_uses_require_tenant_read():
    dep = _get_dependency(get_location_tree, "current_user")
    assert dep is require_tenant_read


def test_get_location_uses_require_tenant_read():
    dep = _get_dependency(get_location, "current_user")
    assert dep is require_tenant_read


def test_get_location_children_uses_require_tenant_read():
    dep = _get_dependency(get_location_children, "current_user")
    assert dep is require_tenant_read


def test_get_location_uses_location_id_param():
    sig = inspect.signature(get_location)
    assert "ubicacion_id" in sig.parameters


def test_update_location_uses_location_id_param():
    sig = inspect.signature(update_location)
    assert "ubicacion_id" in sig.parameters


def test_delete_location_uses_location_id_param():
    sig = inspect.signature(delete_location)
    assert "ubicacion_id" in sig.parameters


def test_get_location_children_uses_location_id_param():
    sig = inspect.signature(get_location_children)
    assert "ubicacion_id" in sig.parameters


def test_create_location_keeps_require_permission():
    from app.domain.enums import PermissionModule
    dep = _get_dependency(create_location, "current_user")
    assert dep is not None
    assert callable(dep)


def test_update_location_keeps_require_permission():
    dep = _get_dependency(update_location, "current_user")
    assert dep is not None
    assert callable(dep)
