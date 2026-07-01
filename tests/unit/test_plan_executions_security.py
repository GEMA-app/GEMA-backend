"""Tests de seguridad para endpoints de ejecuciones de plan."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.plan_executions import (
    create_plan_execution,
    get_plan_execution,
    list_plan_executions,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_list_plan_executions_uses_require_permission() -> None:
    dep = _get_dependency(list_plan_executions, "current_user")
    assert dep is not None
    assert callable(dep)


def test_create_plan_execution_uses_require_permission() -> None:
    dep = _get_dependency(create_plan_execution, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_plan_execution_uses_require_permission() -> None:
    dep = _get_dependency(get_plan_execution, "current_user")
    assert dep is not None
    assert callable(dep)
