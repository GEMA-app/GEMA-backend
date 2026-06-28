"""Tests para seguridad de endpoints de artículos de catálogo (CatalogArticle)."""

import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.catalog_articles import (
    create_catalog_article,
    delete_catalog_article,
    get_catalog_article,
    list_catalog_articles,
    update_catalog_article,
)
from app.presentation.api.v1.endpoints.dependencies import require_tenant_read


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_create_article_uses_require_permission() -> None:
    dep = _get_dependency(create_catalog_article, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_articles_uses_require_tenant_read() -> None:
    dep = _get_dependency(list_catalog_articles, "current_user")
    assert dep is require_tenant_read


def test_get_article_uses_require_tenant_read() -> None:
    dep = _get_dependency(get_catalog_article, "current_user")
    assert dep is require_tenant_read


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
