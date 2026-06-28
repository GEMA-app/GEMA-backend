"""Tests for security of technical interventions endpoints."""

import inspect
from collections.abc import Callable
from typing import Any

from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.interventions import (
    create_intervention,
    get_intervention,
    list_interventions,
    update_intervention,
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


def test_create_intervention_security() -> None:
    dep = _get_dependency(create_intervention, "_")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_list_interventions_security() -> None:
    dep = _get_dependency(list_interventions, "_")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "view"


def test_get_intervention_security() -> None:
    dep = _get_dependency(get_intervention, "_")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "view"


def test_update_intervention_security() -> None:
    dep = _get_dependency(update_intervention, "_")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.MAINTENANCE
    assert action == "edit"


def test_interventions_endpoint_ids_convention() -> None:
    # All CRUD endpoints must receive empresa_id and ot_id, and intervention_id (if applicable) with the correct naming convention
    for func in (get_intervention, update_intervention):
        sig = inspect.signature(func)
        assert "empresa_id" in sig.parameters
        assert "ot_id" in sig.parameters
        assert "intervention_id" in sig.parameters

    for func in (create_intervention, list_interventions):
        sig = inspect.signature(func)
        assert "empresa_id" in sig.parameters
        assert "ot_id" in sig.parameters
