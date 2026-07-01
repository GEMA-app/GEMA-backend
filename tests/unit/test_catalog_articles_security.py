"""Tests para seguridad de endpoints de artículos de catálogo (CatalogArticle)."""

import inspect
from collections.abc import Callable
from typing import Any

from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.catalog_articles import (
    create_catalog_article,
    delete_catalog_article,
    get_catalog_article,
    list_catalog_articles,
    update_catalog_article,
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


def test_create_article_uses_require_permission() -> None:
    dep = _get_dependency(create_catalog_article, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_articles_uses_require_permission() -> None:
    dep = _get_dependency(list_catalog_articles, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.ADMIN
    assert action == "view"


def test_get_article_uses_require_permission() -> None:
    dep = _get_dependency(get_catalog_article, "current_user")
    assert dep is not None
    assert callable(dep)
    module, action = _get_permission_details(dep)
    assert module == PermissionModule.ADMIN
    assert action == "view"


def test_update_article_uses_require_permission() -> None:
    dep = _get_dependency(update_catalog_article, "current_user")
    assert dep is not None
    assert callable(dep)


def test_delete_article_uses_require_permission() -> None:
    dep = _get_dependency(delete_catalog_article, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_article_uses_articulo_id_param() -> None:
    sig = inspect.signature(get_catalog_article)
    assert "articulo_id" in sig.parameters


def test_update_article_uses_articulo_id_param() -> None:
    sig = inspect.signature(update_catalog_article)
    assert "articulo_id" in sig.parameters


def test_delete_article_uses_articulo_id_param() -> None:
    sig = inspect.signature(delete_catalog_article)
    assert "articulo_id" in sig.parameters
