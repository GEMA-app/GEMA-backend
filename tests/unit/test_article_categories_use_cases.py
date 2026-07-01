"""Tests para los casos de uso de categorías de artículos (ArticleCategory)."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.article_category_dtos import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from app.application.use_cases.article_category.create_article_category import (
    CreateArticleCategoryUseCase,
)
from app.application.use_cases.article_category.delete_article_category import (
    DeleteArticleCategoryUseCase,
)
from app.application.use_cases.article_category.get_article_category_by_id import (
    GetArticleCategoryByIdUseCase,
)
from app.application.use_cases.article_category.list_article_category import (
    ListArticleCategoriesUseCase,
)
from app.application.use_cases.article_category.update_article_category import (
    UpdateArticleCategoryUseCase,
)
from app.domain.entities.article_category import ArticleCategory
from app.domain.exceptions import (
    ArticleCategoryNameExistsError,
    ArticleCategoryNotFoundError,
    ValidationError,
)


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.article_categories = MagicMock()
    uow.article_categories.save = AsyncMock()
    uow.article_categories.get_by_id = AsyncMock()
    uow.article_categories.get_by_name = AsyncMock()
    uow.article_categories.get_all_by_company = AsyncMock()
    uow.article_categories.delete = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCreateArticleCategoryUseCase:

    async def test_create_category_success(self, mock_uow: Any) -> None:
        mock_uow.article_categories.get_by_name.return_value = None
        use_case = CreateArticleCategoryUseCase(uow=mock_uow)

        request = CreateCategoryRequest(
            name="Herramientas Eléctricas",
            description="Taladros, sierras y pulidoras",
        )
        empresa_id = str(uuid4())

        res = await use_case.execute(empresa_id, request)

        assert res.name == "Herramientas Eléctricas"
        assert res.description == "Taladros, sierras y pulidoras"
        assert res.version == 1
        assert mock_uow.article_categories.save.called
        assert mock_uow.commit.called

    async def test_create_category_duplicate_name_raises_error(self, mock_uow: Any) -> None:
        mock_uow.article_categories.get_by_name.return_value = MagicMock()
        use_case = CreateArticleCategoryUseCase(uow=mock_uow)

        request = CreateCategoryRequest(
            name="Duplicado",
            description="Alguna descripción",
        )
        empresa_id = str(uuid4())

        with pytest.raises(ArticleCategoryNameExistsError):
            await use_case.execute(empresa_id, request)

        assert not mock_uow.article_categories.save.called
        assert not mock_uow.commit.called

    async def test_create_category_empty_name_raises_validation_error(self, mock_uow: Any) -> None:
        mock_uow.article_categories.get_by_name.return_value = None
        use_case = CreateArticleCategoryUseCase(uow=mock_uow)
        request = CreateCategoryRequest(name="  ", description="Valores vacíos")
        empresa_id = str(uuid4())

        with pytest.raises(ValidationError):
            await use_case.execute(empresa_id, request)


class TestUpdateArticleCategoryUseCase:

    async def test_update_category_all_fields_success(self, mock_uow: Any) -> None:
        empresa_id = uuid4()
        category_id = uuid4()
        existing_category = ArticleCategory.create(
            id=category_id,
            empresa_id=empresa_id,
            name="Nombre Viejo",
            description="Descripcion vieja",
        )
        mock_uow.article_categories.get_by_id.return_value = existing_category
        mock_uow.article_categories.get_by_name.return_value = None

        use_case = UpdateArticleCategoryUseCase(uow=mock_uow)
        request = UpdateCategoryRequest(
            name="Nombre Nuevo",
            description="Descripcion nueva",
        )

        res = await use_case.execute(str(empresa_id), category_id, request)

        assert res.name == "Nombre Nuevo"
        assert res.description == "Descripcion nueva"
        assert mock_uow.article_categories.save.called
        assert mock_uow.commit.called

    async def test_update_category_clear_description_success(self, mock_uow: Any) -> None:
        empresa_id = uuid4()
        category_id = uuid4()
        existing_category = ArticleCategory.create(
            id=category_id,
            empresa_id=empresa_id,
            name="Nombre",
            description="Descripcion existente",
        )
        mock_uow.article_categories.get_by_id.return_value = existing_category

        use_case = UpdateArticleCategoryUseCase(uow=mock_uow)
        request = UpdateCategoryRequest(
            description=None,
            _fields_set=frozenset(["description"])
        )

        res = await use_case.execute(str(empresa_id), category_id, request)

        assert res.description is None
        assert mock_uow.article_categories.save.called

    async def test_update_category_duplicate_name_raises_error(self, mock_uow: Any) -> None:
        empresa_id = uuid4()
        category_id = uuid4()
        existing_category = ArticleCategory.create(
            id=category_id,
            empresa_id=empresa_id,
            name="Nombre Viejo",
            description="Descripcion",
        )
        mock_uow.article_categories.get_by_id.return_value = existing_category
        mock_uow.article_categories.get_by_name.return_value = MagicMock()

        use_case = UpdateArticleCategoryUseCase(uow=mock_uow)
        request = UpdateCategoryRequest(
            name="Nombre Existente",
        )

        with pytest.raises(ArticleCategoryNameExistsError):
            await use_case.execute(str(empresa_id), category_id, request)

    async def test_update_category_not_found_raises_error(self, mock_uow: Any) -> None:
        mock_uow.article_categories.get_by_id.return_value = None
        use_case = UpdateArticleCategoryUseCase(uow=mock_uow)
        request = UpdateCategoryRequest(name="Nombre")

        with pytest.raises(ArticleCategoryNotFoundError):
            await use_case.execute(str(uuid4()), uuid4(), request)


class TestGetArticleCategoryByIdUseCase:

    async def test_get_category_by_id_success(self, mock_uow: Any) -> None:
        empresa_id = uuid4()
        category_id = uuid4()
        category = ArticleCategory.create(
            id=category_id,
            empresa_id=empresa_id,
            name="Electrónica",
            description="Componentes y placas",
        )
        mock_uow.article_categories.get_by_id.return_value = category

        use_case = GetArticleCategoryByIdUseCase(uow=mock_uow)
        res = await use_case.execute(str(empresa_id), category_id)

        assert res.id == category_id
        assert res.name == "Electrónica"
        assert not mock_uow.commit.called

    async def test_get_category_by_id_not_found_raises_error(self, mock_uow: Any) -> None:
        mock_uow.article_categories.get_by_id.return_value = None
        use_case = GetArticleCategoryByIdUseCase(uow=mock_uow)

        with pytest.raises(ArticleCategoryNotFoundError):
            await use_case.execute(str(uuid4()), uuid4())


class TestListArticleCategoriesUseCase:

    async def test_get_all_categories_by_company(self, mock_uow: Any) -> None:
        empresa_id = uuid4()
        categories = [
            ArticleCategory.create(uuid4(), empresa_id, "Cat 1", "Desc 1"),
            ArticleCategory.create(uuid4(), empresa_id, "Cat 2", "Desc 2"),
        ]
        mock_uow.article_categories.get_all_by_company.return_value = categories

        use_case = ListArticleCategoriesUseCase(uow=mock_uow)
        res = await use_case.execute(str(empresa_id))

        assert len(res) == 2
        assert res[0].name == "Cat 1"
        assert res[1].name == "Cat 2"
        # No se realiza commit en consultas de solo lectura
        assert not mock_uow.commit.called


class TestDeleteArticleCategoryUseCase:

    async def test_delete_category_success(self, mock_uow: Any) -> None:
        empresa_id = uuid4()
        category_id = uuid4()
        category = ArticleCategory.create(
            id=category_id,
            empresa_id=empresa_id,
            name="Borrable",
            description="Se eliminará",
        )
        mock_uow.article_categories.get_by_id.return_value = category

        use_case = DeleteArticleCategoryUseCase(uow=mock_uow)
        await use_case.execute(str(empresa_id), category_id)

        mock_uow.article_categories.delete.assert_called_once_with(category_id, empresa_id)
        assert mock_uow.commit.called

    async def test_delete_category_not_found_raises_error(self, mock_uow: Any) -> None:
        mock_uow.article_categories.get_by_id.return_value = None
        use_case = DeleteArticleCategoryUseCase(uow=mock_uow)

        with pytest.raises(ArticleCategoryNotFoundError):
            await use_case.execute(str(uuid4()), uuid4())

        assert not mock_uow.article_categories.delete.called
        assert not mock_uow.commit.called
