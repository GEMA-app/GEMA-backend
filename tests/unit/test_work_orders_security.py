"""Tests for security of work orders endpoints."""

import inspect
from collections.abc import Callable
from typing import Any

from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.work_orders import (
    assign_technician,
    change_work_order_status,
    create_work_order,
    delete_work_order,
    get_work_order,
    get_work_order_status_history,
    list_work_orders,
    remove_technician,
    update_work_order,
    validate_work_order,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def _get_permission_details(dep: Any) -> tuple[PermissionModule | None, str | None]:
    if not dep or not hasattr(dep, "__closure__") or not dep.__closure__:
        return None, None
    module = None
    action = None
    for cell in dep.__closure__:
        contents = cell.cell_contents
        if isinstance(contents, PermissionModule):
            module = contents
        elif isinstance(contents, str) and contents in ("create", "view", "edit", "delete"):
            action = contents
    return module, action


def test_create_work_order_security() -> None:
    dep = _get_dependency(create_work_order, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "create"


def test_list_work_orders_security() -> None:
    dep = _get_dependency(list_work_orders, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "view"


def test_get_work_order_security() -> None:
    dep = _get_dependency(get_work_order, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "view"


def test_update_work_order_security() -> None:
    dep = _get_dependency(update_work_order, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_delete_work_order_security() -> None:
    dep = _get_dependency(delete_work_order, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "delete"


def test_change_work_order_status_security() -> None:
    dep = _get_dependency(change_work_order_status, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_assign_technician_security() -> None:
    dep = _get_dependency(assign_technician, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_remove_technician_security() -> None:
    dep = _get_dependency(remove_technician, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_validate_work_order_security() -> None:
    dep = _get_dependency(validate_work_order, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_get_work_order_status_history_security() -> None:
    dep = _get_dependency(get_work_order_status_history, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "view"
