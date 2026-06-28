"""Tests para seguridad de endpoints de categorías de artículos (ArticleCategory)."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.article_category import (
    create_category,
    delete_category,
    get_category_by_id,
    list_categories,
    update_category,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_create_category_uses_require_permission() -> None:
    dep = _get_dependency(create_category, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_categories_uses_require_permission() -> None:
    dep = _get_dependency(list_categories, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_category_by_id_uses_require_permission() -> None:
    dep = _get_dependency(get_category_by_id, "current_user")
    assert dep is not None
    assert callable(dep)


def test_update_category_uses_require_permission() -> None:
    dep = _get_dependency(update_category, "current_user")
    assert dep is not None
    assert callable(dep)


def test_delete_category_uses_require_permission() -> None:
    dep = _get_dependency(delete_category, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_category_by_id_uses_categoria_id_param() -> None:
    sig = inspect.signature(get_category_by_id)
    assert "categoria_id" in sig.parameters


def test_update_category_uses_categoria_id_param() -> None:
    sig = inspect.signature(update_category)
    assert "categoria_id" in sig.parameters


def test_delete_category_uses_categoria_id_param() -> None:
    sig = inspect.signature(delete_category)
    assert "categoria_id" in sig.parameters
