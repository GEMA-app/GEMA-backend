"""Tests for security of failure reports endpoints."""

import inspect
from collections.abc import Callable
from typing import Any

from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.failure_reports import (
    create_failure_report,
    delete_failure_report,
    get_failure_report,
    list_failure_reports,
    update_failure_report,
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


def test_create_failure_report_security() -> None:
    dep = _get_dependency(create_failure_report, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "create"


def test_list_failure_reports_security() -> None:
    dep = _get_dependency(list_failure_reports, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "view"


def test_get_failure_report_security() -> None:
    dep = _get_dependency(get_failure_report, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "view"


def test_update_failure_report_security() -> None:
    dep = _get_dependency(update_failure_report, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_delete_failure_report_security() -> None:
    dep = _get_dependency(delete_failure_report, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "delete"


def test_failure_reports_endpoint_ids_convention() -> None:
    # All CRUD endpoints must receive empresa_id and reporte_id (if applicable) with the correct naming convention
    for func in (get_failure_report, update_failure_report, delete_failure_report):
        sig = inspect.signature(func)
        assert "empresa_id" in sig.parameters
        assert "reporte_id" in sig.parameters

    for func in (create_failure_report, list_failure_reports):
        sig = inspect.signature(func)
        assert "empresa_id" in sig.parameters
