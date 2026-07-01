"""Tests para verificar la seguridad RBAC y parámetros de path en endpoints de inventario y movimientos."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.inventory_part import (
    create_inventory_movement,
    create_inventory_part,
    delete_inventory_part,
    get_inventory_movement,
    get_inventory_part,
    list_inventory_movements,
    list_inventory_parts,
    update_inventory_part,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_get_inventory_part_uses_require_permission() -> None:
    dep = _get_dependency(get_inventory_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_inventory_parts_uses_require_permission() -> None:
    dep = _get_dependency(list_inventory_parts, "current_user")
    assert dep is not None
    assert callable(dep)


def test_create_inventory_part_uses_require_permission() -> None:
    dep = _get_dependency(create_inventory_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_update_inventory_part_uses_require_permission() -> None:
    dep = _get_dependency(update_inventory_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_delete_inventory_part_uses_require_permission() -> None:
    dep = _get_dependency(delete_inventory_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_create_inventory_movement_uses_require_permission() -> None:
    dep = _get_dependency(create_inventory_movement, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_inventory_movements_uses_require_permission() -> None:
    dep = _get_dependency(list_inventory_movements, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_inventory_movement_uses_require_permission() -> None:
    dep = _get_dependency(get_inventory_movement, "current_user")
    assert dep is not None
    assert callable(dep)


def test_inventory_endpoints_use_correct_path_params() -> None:
    endpoints_with_part_id = [
        get_inventory_part,
        update_inventory_part,
        delete_inventory_part,
        create_inventory_movement,
        list_inventory_movements,
        get_inventory_movement,
    ]
    for endpoint in endpoints_with_part_id:
        sig = inspect.signature(endpoint)
        assert "empresa_id" in sig.parameters
        assert "repuesto_id" in sig.parameters

    endpoints_without_part_id = [
        create_inventory_part,
        list_inventory_parts,
    ]
    for endpoint in endpoints_without_part_id:
        sig = inspect.signature(endpoint)
        assert "empresa_id" in sig.parameters
        assert "repuesto_id" not in sig.parameters
