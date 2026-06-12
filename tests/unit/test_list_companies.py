"""Tests para ListCompaniesUseCase."""
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.companies = MagicMock()
    uow.companies.list_all = AsyncMock()
    uow.companies.get_by_id = AsyncMock()
    return uow


class TestListCompanies:

    async def test_execute_without_company_id(self, mock_uow: Any) -> None:
        from app.application.use_cases.company.list_companies import ListCompaniesUseCase

        mock_company = MagicMock()
        mock_company.id = str(uuid4())
        mock_company.nombre = "Empresa A"
        mock_company.slug = MagicMock()
        mock_company.slug.value = "empresa-a"
        mock_company.rif = "J-123"
        mock_company.email_contacto = "a@test.com"
        mock_company.estado = MagicMock()
        mock_company.estado.value = "activa"
        mock_company.plan_id = None
        mock_company.trial_hasta = None

        mock_uow.companies.list_all.return_value = ([mock_company], 1)

        use_case = ListCompaniesUseCase(uow=mock_uow)
        companies, total = await use_case.execute(0, 10)

        mock_uow.companies.list_all.assert_called_once_with(0, 10)
        mock_uow.companies.get_by_id.assert_not_called()
        assert total == 1
        assert len(companies) == 1
        assert companies[0].nombre == "Empresa A"

    async def test_execute_with_company_id_found(self, mock_uow: Any) -> None:
        from app.application.use_cases.company.list_companies import ListCompaniesUseCase

        company_uuid = str(uuid4())
        mock_company = MagicMock()
        mock_company.id = company_uuid
        mock_company.nombre = "Empresa A"
        mock_company.slug = MagicMock()
        mock_company.slug.value = "empresa-a"
        mock_company.rif = "J-123"
        mock_company.email_contacto = "a@test.com"
        mock_company.estado = MagicMock()
        mock_company.estado.value = "activa"
        mock_company.plan_id = None
        mock_company.trial_hasta = None

        mock_uow.companies.get_by_id.return_value = mock_company

        use_case = ListCompaniesUseCase(uow=mock_uow)
        companies, total = await use_case.execute(0, 10, company_id=company_uuid)

        mock_uow.companies.get_by_id.assert_called_once()
        mock_uow.companies.list_all.assert_not_called()
        assert total == 1
        assert len(companies) == 1
        assert companies[0].nombre == "Empresa A"

    async def test_execute_with_company_id_not_found(self, mock_uow: Any) -> None:
        from app.application.use_cases.company.list_companies import ListCompaniesUseCase

        company_uuid = str(uuid4())
        mock_uow.companies.get_by_id.return_value = None

        use_case = ListCompaniesUseCase(uow=mock_uow)
        companies, total = await use_case.execute(0, 10, company_id=company_uuid)

        mock_uow.companies.get_by_id.assert_called_once()
        mock_uow.companies.list_all.assert_not_called()
        assert total == 0
        assert companies == []
