"""Fábricas de dependencias para los casos de uso de artículos de catálogo."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.catalog_article import (
    CreateCatalogArticleUseCase,
    DeleteCatalogArticleUseCase,
    GetCatalogArticleUseCase,
    UpdateCatalogArticleUseCase,
)
from app.application.use_cases.catalog_article.list_catalog_article import (
    ListCatalogArticlesUseCase,
)
from app.composition.container.common import get_uow


async def get_create_catalog_article_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateCatalogArticleUseCase:
    """Fábrica de dependencias para el caso de uso de creación de artículo de catálogo."""
    return CreateCatalogArticleUseCase(uow)


async def get_catalog_article_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetCatalogArticleUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de artículo de catálogo."""
    return GetCatalogArticleUseCase(uow)


async def get_list_catalog_articles_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListCatalogArticlesUseCase:
    """Fábrica de dependencias para el caso de uso de listado de artículos de catálogo."""
    return ListCatalogArticlesUseCase(uow)


async def get_update_catalog_article_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateCatalogArticleUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de artículo de catálogo."""
    return UpdateCatalogArticleUseCase(uow)


async def get_delete_catalog_article_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteCatalogArticleUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de artículo de catálogo."""
    return DeleteCatalogArticleUseCase(uow)
