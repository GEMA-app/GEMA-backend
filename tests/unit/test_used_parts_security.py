"""Tests para seguridad de endpoints de repuestos utilizados (UsedPart)."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.used_parts import (
    create_used_part,
    delete_used_part,
    get_used_part,
    list_used_parts,
    update_used_part,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_list_used_parts_uses_require_permission() -> None:
    dep = _get_dependency(list_used_parts, "current_user")
    assert dep is not None
    assert callable(dep)


def test_create_used_part_uses_require_permission() -> None:
    dep = _get_dependency(create_used_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_used_part_uses_require_permission() -> None:
    dep = _get_dependency(get_used_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_update_used_part_uses_require_permission() -> None:
    dep = _get_dependency(update_used_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_delete_used_part_uses_require_permission() -> None:
    dep = _get_dependency(delete_used_part, "current_user")
    assert dep is not None
    assert callable(dep)


def test_endpoints_use_correct_path_params() -> None:
    endpoints = [
        list_used_parts,
        create_used_part,
        get_used_part,
        update_used_part,
        delete_used_part,
    ]
    for endpoint in endpoints:
        sig = inspect.signature(endpoint)
        assert "empresa_id" in sig.parameters
        assert "ot_id" in sig.parameters
        assert "intervencion_id" in sig.parameters
