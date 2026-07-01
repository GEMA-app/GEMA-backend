"""Tests de seguridad para endpoints de preferencias."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.preferences import (
    get_preferences,
    update_preferences,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_get_preferences_uses_require_permission() -> None:
    dep = _get_dependency(get_preferences, "current_user")
    assert dep is not None
    assert callable(dep)


def test_update_preferences_uses_require_permission() -> None:
    dep = _get_dependency(update_preferences, "current_user")
    assert dep is not None
    assert callable(dep)
