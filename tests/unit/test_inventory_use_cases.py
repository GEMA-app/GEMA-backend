"""Tests para casos de uso de inventario (InventoryPart) y movimientos (InventoryEntry)."""

from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.inventory_part_dtos import (
    CreateInventoryEntryRequest,
    CreateInventoryPartRequest,
    UpdateInventoryPartRequest,
)
from app.application.use_cases.inventory_part.create_inventory_entry import (
    CreateInventoryEntryUseCase,
)
from app.application.use_cases.inventory_part.create_inventory_part import (
    CreateInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.delete_inventory_part import (
    DeleteInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.get_inventory_entry import (
    GetInventoryEntryUseCase,
)
from app.application.use_cases.inventory_part.get_inventory_part import GetInventoryPartUseCase
from app.application.use_cases.inventory_part.list_inventory_entries import (
    ListInventoryEntriesUseCase,
)
from app.application.use_cases.inventory_part.list_inventory_parts import ListInventoryPartsUseCase
from app.application.use_cases.inventory_part.update_inventory_part import (
    UpdateInventoryPartUseCase,
)
from app.domain.entities.inventory_entry import InventoryEntry
from app.domain.entities.inventory_part import InventoryPart
from app.domain.exceptions import (
    InvalidStockError,
    InventoryEntryNotFoundError,
    InventoryPartNotFoundError,
    StaleDataError,
)
from app.domain.value_objects import ArticleId, CompanyId, ProviderId, RepuestoId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    
    uow.inventory_parts = MagicMock()
    uow.inventory_parts.save = AsyncMock()
    uow.inventory_parts.get_by_id = AsyncMock()
    uow.inventory_parts.get_all_by_empresa = AsyncMock()
    uow.inventory_parts.delete = AsyncMock()

    uow.inventory_entries = MagicMock()
    uow.inventory_entries.save = AsyncMock()
    uow.inventory_entries.get_by_id = AsyncMock()
    uow.inventory_entries.get_all_by_repuesto = AsyncMock()
    
    uow.commit = AsyncMock()
    uow.session = None
    return uow


class TestInventoryPartUseCases:

    async def test_create_inventory_part(self, mock_uow: Any) -> None:
        use_case = CreateInventoryPartUseCase(uow=mock_uow)
        company_id = str(uuid4())
        articulo_id = str(uuid4())
        proveedor_id = str(uuid4())

        request = CreateInventoryPartRequest(
            articulo_id=articulo_id,
            proveedor_id=proveedor_id,
            stock_minimo=10,
            ubicacion_almacen="Almacen A-1",
            precio_unitario=Decimal("25.50"),
            stock_inicial=50,
            moneda="USD",
        )

        response = await use_case.execute(company_id, request)

        assert response.stock_actual == 50
        assert response.stock_minimo == 10
        assert response.ubicacion_almacen == "Almacen A-1"
        assert response.precio_unitario == Decimal("25.50")
        mock_uow.inventory_parts.save.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_get_inventory_part_success(self, mock_uow: Any) -> None:
        use_case = GetInventoryPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=10,
            stock_minimo=2,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("15.00"),
            moneda="USD",
        )
        mock_uow.inventory_parts.get_by_id.return_value = part

        response = await use_case.execute(str(company_id.value), str(part_id.value))

        assert response.id == str(part_id.value)
        assert response.stock_actual == 10
        mock_uow.inventory_parts.get_by_id.assert_called_once_with(part_id, company_id)

    async def test_get_inventory_part_not_found(self, mock_uow: Any) -> None:
        use_case = GetInventoryPartUseCase(uow=mock_uow)
        company_id = str(uuid4())
        part_id = str(uuid4())
        mock_uow.inventory_parts.get_by_id.return_value = None

        with pytest.raises(InventoryPartNotFoundError):
            await use_case.execute(company_id, part_id)

    async def test_update_inventory_part_success(self, mock_uow: Any) -> None:
        use_case = UpdateInventoryPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=10,
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("15.00"),
            moneda="USD",
            version=1,
        )
        
        # Simular get_by_id inicial y recarga
        mock_uow.inventory_parts.get_by_id.side_effect = [part, part]

        request = UpdateInventoryPartRequest(stock_minimo=8, version=1)
        response = await use_case.execute(str(company_id.value), str(part_id.value), request)

        assert response.stock_minimo == 8
        mock_uow.inventory_parts.save.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_update_inventory_part_stale_data(self, mock_uow: Any) -> None:
        use_case = UpdateInventoryPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=10,
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("15.00"),
            moneda="USD",
            version=2,
        )
        mock_uow.inventory_parts.get_by_id.return_value = part

        request = UpdateInventoryPartRequest(stock_minimo=8, version=1)
        with pytest.raises(StaleDataError):
            await use_case.execute(str(company_id.value), str(part_id.value), request)

    async def test_delete_inventory_part_success(self, mock_uow: Any) -> None:
        use_case = DeleteInventoryPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=0, # Stock actual es 0
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("15.00"),
            moneda="USD",
        )
        mock_uow.inventory_parts.get_by_id.return_value = part
        mock_uow.inventory_entries.get_all_by_repuesto.return_value = [] # Sin movimientos

        await use_case.execute(str(company_id.value), str(part_id.value))

        mock_uow.inventory_parts.delete.assert_called_once_with(part_id, company_id)
        mock_uow.commit.assert_called_once()

    async def test_delete_inventory_part_fails_stock_not_zero(self, mock_uow: Any) -> None:
        use_case = DeleteInventoryPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=5, # Stock actual > 0
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("15.00"),
            moneda="USD",
        )
        mock_uow.inventory_parts.get_by_id.return_value = part

        with pytest.raises(InvalidStockError):
            await use_case.execute(str(company_id.value), str(part_id.value))

    async def test_delete_inventory_part_fails_has_movements(self, mock_uow: Any) -> None:
        use_case = DeleteInventoryPartUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=0,
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("15.00"),
            moneda="USD",
        )
        mock_uow.inventory_parts.get_by_id.return_value = part
        
        # Simular que tiene al menos un movimiento
        movement = InventoryEntry(
            id=uuid4(),
            empresa_id=company_id,
            repuesto_id=part_id.value,
            ordenes_trabajo_id=None,
            usuario_id=None,
            cantidad=10,
            tipo_movimiento="entrada",
            precio_unitario=Decimal("15.00"),
        )
        mock_uow.inventory_entries.get_all_by_repuesto.return_value = [movement]

        with pytest.raises(InvalidStockError):
            await use_case.execute(str(company_id.value), str(part_id.value))


class TestInventoryEntryUseCases:

    async def test_create_inventory_movement_entrada(self, mock_uow: Any) -> None:
        use_case = CreateInventoryEntryUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=50,
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("10.00"),
            moneda="USD",
        )
        mock_uow.inventory_parts.get_by_id.return_value = part

        request = CreateInventoryEntryRequest(
            repuesto_id=str(part_id.value),
            movement_type="entrada",
            quantity=20,
            work_order_id=None,
            usuario_id=str(uuid4()),
            reason="Compra inicial",
        )

        response = await use_case.execute(str(company_id.value), request)

        assert response.quantity == 20
        assert response.movement_type == "entrada"
        assert part.stock_actual == 70  # 50 + 20
        mock_uow.inventory_entries.save.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_inventory_movement_salida_insufficient_stock(self, mock_uow: Any) -> None:
        use_case = CreateInventoryEntryUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=10,
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("10.00"),
            moneda="USD",
        )
        mock_uow.inventory_parts.get_by_id.return_value = part

        request = CreateInventoryEntryRequest(
            repuesto_id=str(part_id.value),
            movement_type="salida",
            quantity=15,  # 15 > 10 stock_actual
            work_order_id=None,
            usuario_id=None,
            reason="Consumo mantenimiento",
        )

        with pytest.raises(InvalidStockError):
            await use_case.execute(str(company_id.value), request)

    async def test_list_inventory_entries_success(self, mock_uow: Any) -> None:
        use_case = ListInventoryEntriesUseCase(uow=mock_uow)
        company_id = CompanyId(uuid4())
        part_id = RepuestoId(uuid4())

        part = InventoryPart(
            id=part_id,
            empresa_id=company_id,
            articulo_id=ArticleId(uuid4()),
            proveedor_id=ProviderId(uuid4()),
            stock_actual=10,
            stock_minimo=5,
            ubicacion_almacen="Pasillo B",
            precio_unitario=Decimal("10.00"),
            moneda="USD",
        )
        mock_uow.inventory_parts.get_by_id.return_value = part

        entry = InventoryEntry(
            id=uuid4(),
            empresa_id=company_id,
            repuesto_id=part_id.value,
            ordenes_trabajo_id=None,
            usuario_id=None,
            cantidad=5,
            tipo_movimiento="entrada",
            precio_unitario=Decimal("10.00"),
        )
        mock_uow.inventory_entries.get_all_by_repuesto.return_value = [entry]

        response = await use_case.execute(str(company_id.value), str(part_id.value))

        assert len(response) == 1
        assert response[0].quantity == 5
        mock_uow.inventory_entries.get_all_by_repuesto.assert_called_once()

    async def test_get_inventory_entry_not_found(self, mock_uow: Any) -> None:
        use_case = GetInventoryEntryUseCase(uow=mock_uow)
        company_id = str(uuid4())
        entry_id = str(uuid4())
        mock_uow.inventory_entries.get_by_id.return_value = None

        with pytest.raises(InventoryEntryNotFoundError):
            await use_case.execute(company_id, entry_id)
