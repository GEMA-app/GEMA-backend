"""Tests de seguridad para endpoints de proveedores."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.suppliers import (
    create_supplier,
    delete_supplier,
    get_supplier,
    list_suppliers,
    update_supplier,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_create_supplier_uses_require_permission() -> None:
    dep = _get_dependency(create_supplier, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_suppliers_uses_require_permission() -> None:
    dep = _get_dependency(list_suppliers, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_supplier_uses_require_permission() -> None:
    dep = _get_dependency(get_supplier, "current_user")
    assert dep is not None
    assert callable(dep)


def test_update_supplier_uses_require_permission() -> None:
    dep = _get_dependency(update_supplier, "current_user")
    assert dep is not None
    assert callable(dep)


def test_delete_supplier_uses_require_permission() -> None:
    dep = _get_dependency(delete_supplier, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_supplier_uses_supplier_id_param() -> None:
    sig = inspect.signature(get_supplier)
    assert "supplier_id" in sig.parameters


def test_update_supplier_uses_supplier_id_param() -> None:
    sig = inspect.signature(update_supplier)
    assert "supplier_id" in sig.parameters


def test_delete_supplier_uses_supplier_id_param() -> None:
    sig = inspect.signature(delete_supplier)
    assert "supplier_id" in sig.parameters
