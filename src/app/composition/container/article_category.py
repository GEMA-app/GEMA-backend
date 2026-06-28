"""Fábricas de dependencias para el módulo ArticleCategory (Categorías de Catálogo)."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.article_category.create_article_category import (
    CreateArticleCategoryUseCase,
)
from app.application.use_cases.article_category.delete_article_category import (
    DeleteArticleCategoryUseCase,
)
from app.application.use_cases.article_category.get_all_article_categories import (
    GetAllArticleCategoriesUseCase,
)
from app.application.use_cases.article_category.get_article_category_by_id import (
    GetArticleCategoryByIdUseCase,
)
from app.application.use_cases.article_category.update_article_category import (
    UpdateArticleCategoryUseCase,
)
from app.composition.container.common import get_uow


async def get_create_article_category_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateArticleCategoryUseCase:
    """Fábrica para CreateArticleCategoryUseCase."""
    return CreateArticleCategoryUseCase(uow=uow)


async def get_article_category_by_id_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetArticleCategoryByIdUseCase:
    """Fábrica para GetArticleCategoryByIdUseCase."""
    return GetArticleCategoryByIdUseCase(uow=uow)


async def get_all_article_categories_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetAllArticleCategoriesUseCase:
    """Fábrica para GetAllArticleCategoriesUseCase."""
    return GetAllArticleCategoriesUseCase(uow=uow)


async def get_update_article_category_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateArticleCategoryUseCase:
    """Fábrica para UpdateArticleCategoryUseCase."""
    return UpdateArticleCategoryUseCase(uow=uow)


async def get_delete_article_category_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteArticleCategoryUseCase:
    """Fábrica para DeleteArticleCategoryUseCase."""
    return DeleteArticleCategoryUseCase(uow=uow)
