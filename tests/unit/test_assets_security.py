"""Tests de seguridad para endpoints de activos."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.assets import (
    create_asset,
    delete_asset,
    get_asset,
    list_assets,
    update_asset,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_create_asset_uses_require_permission() -> None:
    dep = _get_dependency(create_asset, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_assets_uses_require_permission() -> None:
    dep = _get_dependency(list_assets, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_asset_uses_require_permission() -> None:
    dep = _get_dependency(get_asset, "current_user")
    assert dep is not None
    assert callable(dep)


def test_update_asset_uses_require_permission() -> None:
    dep = _get_dependency(update_asset, "current_user")
    assert dep is not None
    assert callable(dep)


def test_delete_asset_uses_require_permission() -> None:
    dep = _get_dependency(delete_asset, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_asset_uses_activo_id_param() -> None:
    sig = inspect.signature(get_asset)
    assert "activo_id" in sig.parameters


def test_update_asset_uses_activo_id_param() -> None:
    sig = inspect.signature(update_asset)
    assert "activo_id" in sig.parameters


def test_delete_asset_uses_activo_id_param() -> None:
    sig = inspect.signature(delete_asset)
    assert "activo_id" in sig.parameters
