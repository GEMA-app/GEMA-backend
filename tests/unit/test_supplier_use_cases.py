"""Tests unitarios para casos de uso de proveedores."""

from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from app.application.dtos.supplier_dtos import (
    CreateSupplierRequest,
    UpdateSupplierRequest,
)
from app.application.use_cases.supplier.create_supplier import CreateSupplierUseCase
from app.application.use_cases.supplier.delete_supplier import DeleteSupplierUseCase
from app.application.use_cases.supplier.get_supplier import GetSupplierUseCase
from app.application.use_cases.supplier.list_suppliers import ListSuppliersUseCase
from app.application.use_cases.supplier.update_supplier import UpdateSupplierUseCase
from app.domain.entities.supplier import Supplier
from app.domain.exceptions.supplier import (
    SupplierHasInventoryPartsError,
    SupplierNotFoundError,
    SupplierRifExistsError,
)


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.suppliers = AsyncMock()
    # Context manager async with
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def empresa_id() -> UUID:
    return uuid4()


@pytest.fixture
def supplier_id() -> UUID:
    return uuid4()


@pytest.fixture
def sample_supplier(empresa_id: UUID, supplier_id: UUID) -> Supplier:
    return Supplier.create(
        id=supplier_id,
        empresa_id=empresa_id,
        name="Proveedor Test",
        rif="J-12345678-9",
        phone="+584141234567",
        email="contacto@test.com",
        contact="Juan Pérez",
    )


class TestCreateSupplierUseCase:
    async def test_create_supplier_success(self, mock_uow, empresa_id):
        dto = CreateSupplierRequest(
            name="Nuevo Proveedor",
            rif="J-87654321-0",
            phone="+584147654321",
            email="nuevo@test.com",
            contact="Maria Lopez",
        )
        # Mock RIF check returns None (no duplicado)
        mock_uow.suppliers.get_by_rif.return_value = None
        # Mock save does nothing
        mock_uow.suppliers.save.return_value = None

        use_case = CreateSupplierUseCase(uow=mock_uow)
        result = await use_case.execute(str(empresa_id), dto)

        assert result.name == "Nuevo Proveedor"
        assert result.rif == "J-87654321-0"
        mock_uow.suppliers.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_create_supplier_duplicate_rif(self, mock_uow, empresa_id, sample_supplier):
        dto = CreateSupplierRequest(
            name="Test", rif="J-11111111-1",
            phone=None, email=None, contact=None,
        )
        mock_uow.suppliers.get_by_rif.return_value = sample_supplier

        use_case = CreateSupplierUseCase(uow=mock_uow)
        with pytest.raises(SupplierRifExistsError):
            await use_case.execute(str(empresa_id), dto)

    async def test_create_supplier_no_rif_validation(self, mock_uow, empresa_id):
        """Sin RIF, no debe llamar a get_by_rif."""
        dto = CreateSupplierRequest(
            name="Sin RIF", rif=None,
            phone=None, email=None, contact=None,
        )
        mock_uow.suppliers.save.return_value = None

        use_case = CreateSupplierUseCase(uow=mock_uow)
        result = await use_case.execute(str(empresa_id), dto)

        mock_uow.suppliers.get_by_rif.assert_not_awaited()
        assert result.name == "Sin RIF"


class TestGetSupplierUseCase:
    async def test_get_supplier_success(self, mock_uow, empresa_id, supplier_id, sample_supplier):
        mock_uow.suppliers.get_by_id.return_value = sample_supplier

        use_case = GetSupplierUseCase(uow=mock_uow)
        result = await use_case.execute(str(empresa_id), supplier_id)

        assert result.id == supplier_id
        assert result.name == "Proveedor Test"
        mock_uow.suppliers.get_by_id.assert_awaited_once_with(supplier_id, empresa_id)

    async def test_get_supplier_not_found(self, mock_uow, empresa_id):
        mock_uow.suppliers.get_by_id.return_value = None

        use_case = GetSupplierUseCase(uow=mock_uow)
        with pytest.raises(SupplierNotFoundError):
            await use_case.execute(str(empresa_id), uuid4())


class TestListSuppliersUseCase:
    async def test_list_suppliers(self, mock_uow, empresa_id, sample_supplier):
        mock_uow.suppliers.get_all_by_company.return_value = [sample_supplier]

        use_case = ListSuppliersUseCase(uow=mock_uow)
        result = await use_case.execute(str(empresa_id))

        assert len(result) == 1
        assert result[0].name == "Proveedor Test"

    async def test_list_suppliers_empty(self, mock_uow, empresa_id):
        mock_uow.suppliers.get_all_by_company.return_value = []

        use_case = ListSuppliersUseCase(uow=mock_uow)
        result = await use_case.execute(str(empresa_id))

        assert len(result) == 0

    async def test_list_suppliers_with_search(self, mock_uow, empresa_id, sample_supplier):
        mock_uow.suppliers.get_all_by_company.return_value = [sample_supplier]

        use_case = ListSuppliersUseCase(uow=mock_uow)
        result = await use_case.execute(str(empresa_id), search="Test")

        assert len(result) == 1
        mock_uow.suppliers.get_all_by_company.assert_awaited_once_with(empresa_id, search="Test", include_inactive=False)


class TestUpdateSupplierUseCase:
    async def test_update_supplier_success(self, mock_uow, empresa_id, supplier_id, sample_supplier):
        dto = UpdateSupplierRequest(
            name="Actualizado", rif="J-99999999-9",
            phone=None, email=None, contact=None, version=1,
            _fields_set=frozenset({"name", "rif"}),
        )
        mock_uow.suppliers.get_by_id.return_value = sample_supplier
        mock_uow.suppliers.get_by_rif.return_value = None
        mock_uow.suppliers.save.return_value = None

        use_case = UpdateSupplierUseCase(uow=mock_uow)
        result = await use_case.execute(str(empresa_id), supplier_id, dto)

        assert result.name == "Actualizado"
        mock_uow.suppliers.save.assert_awaited_once()

    async def test_update_supplier_not_found(self, mock_uow, empresa_id):
        dto = UpdateSupplierRequest(
            name="X", rif="J-1", phone=None, email=None, contact=None,
            version=1, _fields_set=frozenset({"name"}),
        )
        mock_uow.suppliers.get_by_id.return_value = None

        use_case = UpdateSupplierUseCase(uow=mock_uow)
        with pytest.raises(SupplierNotFoundError):
            await use_case.execute(str(empresa_id), uuid4(), dto)


class TestDeleteSupplierUseCase:
    async def test_delete_supplier_success(self, mock_uow, empresa_id, supplier_id, sample_supplier):
        mock_uow.suppliers.get_by_id.return_value = sample_supplier
        mock_uow.suppliers.has_inventory_parts.return_value = False

        use_case = DeleteSupplierUseCase(uow=mock_uow)
        await use_case.execute(str(empresa_id), supplier_id)

        mock_uow.suppliers.delete.assert_awaited_once_with(supplier_id, empresa_id)
        mock_uow.commit.assert_awaited_once()

    async def test_delete_supplier_not_found(self, mock_uow, empresa_id):
        mock_uow.suppliers.get_by_id.return_value = None

        use_case = DeleteSupplierUseCase(uow=mock_uow)
        with pytest.raises(SupplierNotFoundError):
            await use_case.execute(str(empresa_id), uuid4())

    async def test_delete_supplier_has_inventory_parts(self, mock_uow, empresa_id, supplier_id, sample_supplier):
        mock_uow.suppliers.get_by_id.return_value = sample_supplier
        mock_uow.suppliers.has_inventory_parts.return_value = True

        use_case = DeleteSupplierUseCase(uow=mock_uow)
        with pytest.raises(SupplierHasInventoryPartsError):
            await use_case.execute(str(empresa_id), supplier_id)
