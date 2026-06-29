"""Tests para casos de uso de repuestos utilizados (UsedPart)."""

from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.used_part_dtos import (
    CreateUsedPartRequest,
    UpdateUsedPartRequest,
)
from app.application.use_cases.used_part.create_used_part import CreateUsedPartUseCase
from app.application.use_cases.used_part.delete_used_part import DeleteUsedPartUseCase
from app.application.use_cases.used_part.get_used_part import GetUsedPartUseCase
from app.application.use_cases.used_part.list_used_parts import ListUsedPartsUseCase
from app.application.use_cases.used_part.update_used_part import UpdateUsedPartUseCase
from app.domain.entities.used_part import UsedPart
from app.domain.exceptions.used_part import UsedPartNotFoundError
from app.domain.value_objects import CompanyId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.used_parts = MagicMock()
    uow.used_parts.save = AsyncMock()
    uow.used_parts.get_by_id = AsyncMock()
    uow.used_parts.get_by_intervention = AsyncMock()
    uow.used_parts.delete = AsyncMock()
    uow.commit = AsyncMock()
    # Sin sesión real: el bloque de descuento de stock se omite correctamente
    uow.session = None
    return uow


class TestUsedPartUseCases:

    async def test_create_used_part(self, mock_uow: Any) -> None:
        use_case = CreateUsedPartUseCase(uow=mock_uow)
        company_id = str(uuid4())
        intervention_id = uuid4()
        repuesto_id = uuid4()

        request = CreateUsedPartRequest(
            intervencion_id=intervention_id,
            repuesto_id=repuesto_id,
            cantidad_usada=5,
            precio_unitario=Decimal("15.50"),
            moneda="USD",
        )

        response = await use_case.execute(company_id, request)

        assert response.cantidad_usada == 5
        assert response.precio_unitario == Decimal("15.50")
        assert response.moneda == "USD"
        mock_uow.used_parts.save.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_get_used_part_success(self, mock_uow: Any) -> None:
        use_case = GetUsedPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = uuid4()

        part = UsedPart(
            id=part_id,
            empresa_id=company_id,
            intervencion_id=uuid4(),
            repuesto_id=uuid4(),
            cantidad_usada=10,
            precio_unitario=Decimal("20.00"),
            moneda="USD",
        )
        mock_uow.used_parts.get_by_id.return_value = part

        response = await use_case.execute(str(company_id.value), part_id)

        assert response.id == part_id
        assert response.cantidad_usada == 10
        mock_uow.used_parts.get_by_id.assert_called_once_with(part_id, company_id)

    async def test_get_used_part_not_found(self, mock_uow: Any) -> None:
        use_case = GetUsedPartUseCase(uow=mock_uow)
        company_id = str(uuid4())
        part_id = uuid4()
        mock_uow.used_parts.get_by_id.return_value = None

        with pytest.raises(UsedPartNotFoundError):
            await use_case.execute(company_id, part_id)

    async def test_list_used_parts(self, mock_uow: Any) -> None:
        use_case = ListUsedPartsUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        intervention_id = uuid4()

        part = UsedPart(
            id=uuid4(),
            empresa_id=company_id,
            intervencion_id=intervention_id,
            repuesto_id=uuid4(),
            cantidad_usada=2,
            precio_unitario=Decimal("5.00"),
            moneda="USD",
        )
        mock_uow.used_parts.get_by_intervention.return_value = [part]

        response = await use_case.execute(str(company_id.value), intervention_id)

        assert len(response) == 1
        assert response[0].cantidad_usada == 2
        mock_uow.used_parts.get_by_intervention.assert_called_once()

    async def test_update_used_part_success(self, mock_uow: Any) -> None:
        use_case = UpdateUsedPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = uuid4()

        part = UsedPart(
            id=part_id,
            empresa_id=company_id,
            intervencion_id=uuid4(),
            repuesto_id=uuid4(),
            cantidad_usada=10,
            precio_unitario=Decimal("20.00"),
            moneda="USD",
        )
        mock_uow.used_parts.get_by_id.return_value = part

        request = UpdateUsedPartRequest(cantidad_usada=15)
        response = await use_case.execute(str(company_id.value), part_id, request)

        assert response.cantidad_usada == 15
        mock_uow.used_parts.save.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_update_used_part_not_found(self, mock_uow: Any) -> None:
        use_case = UpdateUsedPartUseCase(uow=mock_uow)
        company_id = str(uuid4())
        part_id = uuid4()
        mock_uow.used_parts.get_by_id.return_value = None

        request = UpdateUsedPartRequest(cantidad_usada=15)
        with pytest.raises(UsedPartNotFoundError):
            await use_case.execute(company_id, part_id, request)

    async def test_delete_used_part_success(self, mock_uow: Any) -> None:
        use_case = DeleteUsedPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = uuid4()

        part = UsedPart(
            id=part_id,
            empresa_id=company_id,
            intervencion_id=uuid4(),
            repuesto_id=uuid4(),
            cantidad_usada=10,
            precio_unitario=Decimal("20.00"),
            moneda="USD",
        )
        mock_uow.used_parts.get_by_id.return_value = part

        await use_case.execute(str(company_id.value), part_id)

        mock_uow.used_parts.delete.assert_called_once_with(part_id, company_id)
        mock_uow.commit.assert_called_once()

    async def test_delete_used_part_not_found(self, mock_uow: Any) -> None:
        use_case = DeleteUsedPartUseCase(uow=mock_uow)
        company_id = str(uuid4())
        part_id = uuid4()
        mock_uow.used_parts.get_by_id.return_value = None

        with pytest.raises(UsedPartNotFoundError):
            await use_case.execute(company_id, part_id)
