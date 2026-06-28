"""Tests para los casos de uso de artículos de catálogo (CatalogArticle)."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.catalog_article_dtos import (
    CreateCatalogArticleRequest,
    UpdateCatalogArticleRequest,
)
from app.application.use_cases.catalog_article.create_catalog_article import (
    CreateCatalogArticleUseCase,
)
from app.application.use_cases.catalog_article.delete_catalog_article import (
    DeleteCatalogArticleUseCase,
)
from app.application.use_cases.catalog_article.get_catalog_article import (
    GetCatalogArticleUseCase,
)
from app.application.use_cases.catalog_article.list_catalog_articles import (
    ListCatalogArticlesUseCase,
)
from app.application.use_cases.catalog_article.update_catalog_article import (
    UpdateCatalogArticleUseCase,
)
from app.domain.entities import CatalogArticle
from app.domain.exceptions import (
    CatalogArticleNotFoundError,
    EmptyCatalogArticleNameError,
)
from app.domain.value_objects import CompanyId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.catalog_articles = MagicMock()
    uow.catalog_articles.save = AsyncMock()
    uow.catalog_articles.get_by_company_and_id = AsyncMock()
    uow.catalog_articles.list_by_company = AsyncMock()
    uow.catalog_articles.delete = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCreateCatalogArticleUseCase:

    async def test_create_article_success(self, mock_uow: Any) -> None:
        use_case = CreateCatalogArticleUseCase(uow=mock_uow)
        request = CreateCatalogArticleRequest(
            category_id=str(uuid4()),
            name="Motor trifásico 5HP",
            description="Motor eléctrico de inducción",
            manufacturer="Siemens",
            model="1LA7083",
            unit_of_measure="UNIDAD",
        )
        company_id = str(uuid4())

        res = await use_case.execute(company_id, request)

        assert res.name == "Motor trifásico 5HP"
        assert res.manufacturer == "Siemens"
        assert res.model == "1LA7083"
        assert mock_uow.catalog_articles.save.called
        assert mock_uow.commit.called

    async def test_create_article_empty_name_raises_error(self, mock_uow: Any) -> None:
        use_case = CreateCatalogArticleUseCase(uow=mock_uow)
        request = CreateCatalogArticleRequest(
            category_id=None,
            name="   ",
        )
        company_id = str(uuid4())

        with pytest.raises(EmptyCatalogArticleNameError):
            await use_case.execute(company_id, request)

        assert not mock_uow.catalog_articles.save.called
        assert not mock_uow.commit.called


class TestUpdateCatalogArticleUseCase:

    async def test_update_article_all_fields_success(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        article_id = uuid4()
        existing = CatalogArticle(
            id=article_id,
            empresa_id=company_id.value,
            category_id=None,
            name="Nombre Viejo",
            description="Vieja",
            manufacturer="Viejo",
            model="Viejo",
            unit_of_measure="UNIDAD",
        )
        mock_uow.catalog_articles.get_by_company_and_id.return_value = existing

        use_case = UpdateCatalogArticleUseCase(uow=mock_uow)
        request = UpdateCatalogArticleRequest(
            name="Nombre Nuevo",
            description="Nueva",
            manufacturer="Nuevo",
            model="Nuevo",
            unit_of_measure="LITRO",
            category_id=str(uuid4()),
        )

        res = await use_case.execute(str(company_id.value), str(article_id), request)

        assert res.name == "Nombre Nuevo"
        assert res.description == "Nueva"
        assert res.manufacturer == "Nuevo"
        assert res.model == "Nuevo"
        assert res.unit_of_measure == "LITRO"
        assert res.category_id == request.category_id
        assert mock_uow.catalog_articles.save.called
        assert mock_uow.commit.called

    async def test_update_article_not_found_raises_error(self, mock_uow: Any) -> None:
        mock_uow.catalog_articles.get_by_company_and_id.return_value = None
        use_case = UpdateCatalogArticleUseCase(uow=mock_uow)
        request = UpdateCatalogArticleRequest(name="Nuevo")

        with pytest.raises(CatalogArticleNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()), request)

        assert not mock_uow.catalog_articles.save.called
        assert not mock_uow.commit.called


class TestGetCatalogArticleUseCase:

    async def test_get_article_success(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        article_id = uuid4()
        article = CatalogArticle(
            id=article_id,
            empresa_id=company_id.value,
            category_id=None,
            name="Compresor",
        )
        mock_uow.catalog_articles.get_by_company_and_id.return_value = article

        use_case = GetCatalogArticleUseCase(uow=mock_uow)
        res = await use_case.execute(str(company_id.value), str(article_id))

        assert res.id == str(article_id)
        assert res.name == "Compresor"
        assert mock_uow.commit.called

    async def test_get_article_not_found_raises_error(self, mock_uow: Any) -> None:
        mock_uow.catalog_articles.get_by_company_and_id.return_value = None
        use_case = GetCatalogArticleUseCase(uow=mock_uow)

        with pytest.raises(CatalogArticleNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()))


class TestListCatalogArticlesUseCase:

    async def test_list_articles(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        articles = [
            CatalogArticle(uuid4(), company_id.value, None, "Art 1"),
            CatalogArticle(uuid4(), company_id.value, None, "Art 2"),
        ]
        mock_uow.catalog_articles.list_by_company.return_value = (articles, 2)

        use_case = ListCatalogArticlesUseCase(uow=mock_uow)
        res, total = await use_case.execute(str(company_id.value))

        assert len(res) == 2
        assert total == 2
        assert res[0].name == "Art 1"
        assert res[1].name == "Art 2"
        assert mock_uow.commit.called


class TestDeleteCatalogArticleUseCase:

    async def test_delete_article_success(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        article_id = uuid4()
        article = CatalogArticle(
            id=article_id,
            empresa_id=company_id.value,
            category_id=None,
            name="Borrable",
        )
        mock_uow.catalog_articles.get_by_company_and_id.return_value = article

        use_case = DeleteCatalogArticleUseCase(uow=mock_uow)
        await use_case.execute(str(company_id.value), str(article_id))

        assert mock_uow.catalog_articles.delete.called
        assert mock_uow.commit.called

    async def test_delete_article_not_found_raises_error(self, mock_uow: Any) -> None:
        mock_uow.catalog_articles.get_by_company_and_id.return_value = None
        use_case = DeleteCatalogArticleUseCase(uow=mock_uow)

        with pytest.raises(CatalogArticleNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()))

        assert not mock_uow.catalog_articles.delete.called
        assert not mock_uow.commit.called
