"""Tests para casos de uso de activos (create_asset, update_asset)."""
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domain.enums import AssetStatus


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.assets = MagicMock()
    uow.assets.save = AsyncMock()
    uow.assets.get_by_id = AsyncMock()
    uow.assets.list_by_company = AsyncMock()
    uow.locations = MagicMock()
    uow.locations.get_by_id = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCreateAssetNoON:

    async def test_create_asset_eliminated_o_n(self, mock_uow):
        from app.application.dtos.asset_dtos import CreateAssetRequest
        from app.application.use_cases.asset.create_asset import CreateAssetUseCase

        mock_uow.locations.get_by_id.return_value = MagicMock()
        use_case = CreateAssetUseCase(uow=mock_uow)

        request = CreateAssetRequest(
            articulo_id=str(uuid4()),
            serial_interno="SERIAL-001",
            codigo_activo="CODE-001",
            estado="operativo",
            ubicacion_id=str(uuid4()),
            fecha_adquisicion=None,
            valor_monetario=100.0,
            moneda="USD",
        )

        result = await use_case.execute(str(uuid4()), request)

        mock_uow.assets.list_by_company.assert_not_called()
        assert mock_uow.assets.save.called


class TestUpdateAssetNoON:

    async def test_update_asset_eliminated_o_n_code(self, mock_uow):
        from app.application.dtos.asset_dtos import UpdateAssetRequest
        from app.application.use_cases.asset.update_asset import UpdateAssetUseCase

        mock_asset = MagicMock()
        mock_asset.ubicacion_id = None
        mock_asset.codigo_activo = ""
        mock_asset.serial_interno = ""
        mock_asset.estado = AssetStatus.OPERATIONAL
        mock_asset.fecha_adquisicion = None
        mock_asset.valor_monetario = None
        mock_asset.moneda = None
        mock_uow.assets.get_by_id.return_value = mock_asset

        use_case = UpdateAssetUseCase(uow=mock_uow)
        request = UpdateAssetRequest(
            serial_interno=None,
            codigo_activo="NEW-CODE",
            estado=None,
            ubicacion_id=None,
            fecha_adquisicion=None,
            valor_monetario=None,
            moneda=None,
        )

        result = await use_case.execute(str(uuid4()), str(uuid4()), request)

        mock_uow.assets.list_by_company.assert_not_called()

    async def test_update_asset_eliminated_o_n_serial(self, mock_uow):
        from app.application.dtos.asset_dtos import UpdateAssetRequest
        from app.application.use_cases.asset.update_asset import UpdateAssetUseCase

        mock_asset = MagicMock()
        mock_asset.ubicacion_id = None
        mock_asset.codigo_activo = ""
        mock_asset.serial_interno = ""
        mock_asset.estado = AssetStatus.OPERATIONAL
        mock_asset.fecha_adquisicion = None
        mock_asset.valor_monetario = None
        mock_asset.moneda = None
        mock_uow.assets.get_by_id.return_value = mock_asset

        use_case = UpdateAssetUseCase(uow=mock_uow)
        request = UpdateAssetRequest(
            serial_interno="NEW-SERIAL",
            codigo_activo=None,
            estado=None,
            ubicacion_id=None,
            fecha_adquisicion=None,
            valor_monetario=None,
            moneda=None,
        )

        result = await use_case.execute(str(uuid4()), str(uuid4()), request)

        mock_uow.assets.list_by_company.assert_not_called()


class TestCreateAssetNormalizes:

    async def test_create_asset_normalizes_lowercase(self, mock_uow):
        from app.application.dtos.asset_dtos import CreateAssetRequest
        from app.application.use_cases.asset.create_asset import CreateAssetUseCase

        mock_uow.locations.get_by_id.return_value = MagicMock()
        use_case = CreateAssetUseCase(uow=mock_uow)

        request = CreateAssetRequest(
            articulo_id=str(uuid4()),
            serial_interno="  SERIAL-UPPER-001  ",
            codigo_activo="  CODE-UPPER-001  ",
            estado="operativo",
            ubicacion_id=str(uuid4()),
            fecha_adquisicion=None,
            valor_monetario=100.0,
            moneda="USD",
        )

        result = await use_case.execute(str(uuid4()), request)

        saved_asset = mock_uow.assets.save.call_args[0][0]
        assert saved_asset.serial_interno == "serial-upper-001"
        assert saved_asset.codigo_activo == "code-upper-001"


class TestUpdateAssetNormalizes:

    async def test_update_asset_normalizes_lowercase(self, mock_uow):
        from app.application.dtos.asset_dtos import UpdateAssetRequest
        from app.application.use_cases.asset.update_asset import UpdateAssetUseCase

        mock_asset = MagicMock()
        mock_asset.ubicacion_id = None
        mock_asset.codigo_activo = "old-code"
        mock_asset.serial_interno = "old-serial"
        mock_asset.estado = AssetStatus.OPERATIONAL
        mock_asset.fecha_adquisicion = None
        mock_asset.valor_monetario = None
        mock_asset.moneda = None
        mock_uow.assets.get_by_id.return_value = mock_asset

        use_case = UpdateAssetUseCase(uow=mock_uow)
        request = UpdateAssetRequest(
            serial_interno="  NEW-SERIAL-UPPER  ",
            codigo_activo="  NEW-CODE-UPPER  ",
            estado=None,
            ubicacion_id=None,
            fecha_adquisicion=None,
            valor_monetario=None,
            moneda=None,
        )

        result = await use_case.execute(str(uuid4()), str(uuid4()), request)

        assert mock_asset.serial_interno == "new-serial-upper"
        assert mock_asset.codigo_activo == "new-code-upper"


class TestCreateAssetLocationValidation:

    async def test_create_asset_preserves_location_validation(self, mock_uow):
        from app.application.dtos.asset_dtos import CreateAssetRequest
        from app.application.use_cases.asset.create_asset import CreateAssetUseCase
        from app.domain.exceptions import LocationNotFoundError

        mock_uow.locations.get_by_id.return_value = None
        use_case = CreateAssetUseCase(uow=mock_uow)

        request = CreateAssetRequest(
            articulo_id=str(uuid4()),
            serial_interno="SERIAL-LOC",
            codigo_activo="CODE-LOC",
            estado="operativo",
            ubicacion_id=str(uuid4()),
            fecha_adquisicion=None,
            valor_monetario=100.0,
            moneda="USD",
        )

        with pytest.raises(LocationNotFoundError):
            await use_case.execute(str(uuid4()), request)


class TestUpdateAssetNullification:

    async def test_update_asset_nullifies_location(self, mock_uow):
        from app.application.dtos.asset_dtos import UpdateAssetRequest
        from app.application.use_cases.asset.update_asset import UpdateAssetUseCase
        from app.domain.value_objects import LocationId

        mock_asset = MagicMock()
        mock_asset.ubicacion_id = LocationId(uuid4())
        mock_asset.codigo_activo = "old-code"
        mock_asset.serial_interno = "old-serial"
        mock_asset.estado = AssetStatus.OPERATIONAL
        mock_uow.assets.get_by_id.return_value = mock_asset

        use_case = UpdateAssetUseCase(uow=mock_uow)
        request = UpdateAssetRequest(
            ubicacion_id=None,
            _fields_set=frozenset(["ubicacion_id"])
        )

        await use_case.execute(str(uuid4()), str(uuid4()), request)
        mock_asset.transfer_location.assert_called_once_with(None)
