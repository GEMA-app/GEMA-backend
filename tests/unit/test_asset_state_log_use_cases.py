"""Tests para casos de uso del historial de estados de activos (AssetStateLog)."""

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.asset_dtos import CreateAssetRequest, UpdateAssetRequest
from app.application.use_cases.asset.create_asset import CreateAssetUseCase
from app.application.use_cases.asset.update_asset import UpdateAssetUseCase
from app.application.use_cases.asset_state_log import ListAssetStateLogUseCase
from app.domain.entities import Asset, AssetStateLog
from app.domain.enums import AssetStatus
from app.domain.value_objects import AssetId, CompanyId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.assets = MagicMock()
    uow.assets.save = AsyncMock()
    uow.assets.get_by_id = AsyncMock()

    uow.asset_state_logs = MagicMock()
    uow.asset_state_logs.list_by_asset = AsyncMock()
    uow.asset_state_logs.save = AsyncMock()

    uow.locations = MagicMock()
    uow.locations.get_by_id = AsyncMock()

    uow.commit = AsyncMock()
    return uow


class TestListAssetStateLogUseCase:

    async def test_list_logs_by_asset(self, mock_uow: Any) -> None:
        # Arrange
        company_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        user_id = uuid.uuid4()
        now = datetime.now(UTC)

        log_entity = AssetStateLog(
            id=uuid.uuid4(),
            empresa_id=CompanyId.from_string(company_id),
            activo_id=AssetId.from_string(asset_id),
            estado_anterior=AssetStatus.OPERATIONAL,
            estado_nuevo=AssetStatus.UNDER_MAINTENANCE,
            motivo="Mantenimiento preventivo",
            fecha_cambio=now,
            usuario_id=user_id,
        )

        mock_uow.asset_state_logs.list_by_asset.return_value = [log_entity]

        use_case = ListAssetStateLogUseCase(uow=mock_uow)

        # Act
        results = await use_case.execute(company_id, asset_id)

        # Assert
        assert len(results) == 1
        assert results[0].id == str(log_entity.id)
        assert results[0].estado_anterior == "operativo"
        assert results[0].estado_nuevo == "en_mantenimiento"
        assert results[0].motivo == "Mantenimiento preventivo"
        assert results[0].usuario_id == str(user_id)
        mock_uow.asset_state_logs.list_by_asset.assert_called_once()


class TestAssetLoggingInUseCases:

    async def test_create_asset_saves_initial_state_log(self, mock_uow: Any) -> None:
        # Arrange
        company_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        request = CreateAssetRequest(
            articulo_id=str(uuid.uuid4()),
            serial_interno="SERIAL-111",
            codigo_activo="CODE-111",
            estado="operativo",
            ubicacion_id=None,
            fecha_adquisicion=None,
            valor_monetario=500.0,
            moneda="USD",
        )

        use_case = CreateAssetUseCase(uow=mock_uow)

        # Act
        await use_case.execute(company_id, request, usuario_id_str=user_id)

        # Assert
        assert mock_uow.assets.save.called
        assert mock_uow.asset_state_logs.save.called
        assert mock_uow.commit.called

        # Verificar argumentos de save de log
        saved_log = mock_uow.asset_state_logs.save.call_args[0][0]
        assert isinstance(saved_log, AssetStateLog)
        assert saved_log.estado_anterior is None
        assert saved_log.estado_nuevo == AssetStatus.OPERATIONAL
        assert saved_log.motivo == "Registro inicial del activo"
        assert saved_log.usuario_id == uuid.UUID(user_id)

    async def test_update_asset_state_change_saves_transition_log(self, mock_uow: Any) -> None:
        # Arrange
        company_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        asset = Asset.create(
            empresa_id=CompanyId.from_string(company_id),
            articulo_id=uuid.uuid4(),
            ubicacion_id=None,
            serial_interno="SERIAL-222",
            codigo_activo="CODE-222",
            estado=AssetStatus.OPERATIONAL,
        )
        mock_uow.assets.get_by_id.return_value = asset

        request = UpdateAssetRequest(
            serial_interno=None,
            codigo_activo=None,
            estado="en_mantenimiento",
            ubicacion_id=None,
            fecha_adquisicion=None,
            valor_monetario=None,
            moneda=None,
        )

        use_case = UpdateAssetUseCase(uow=mock_uow)

        # Act
        await use_case.execute(company_id, asset_id, request, usuario_id_str=user_id)

        # Assert
        assert mock_uow.assets.save.called
        assert mock_uow.asset_state_logs.save.called
        assert mock_uow.commit.called

        # Verificar log guardado
        saved_log = mock_uow.asset_state_logs.save.call_args[0][0]
        assert isinstance(saved_log, AssetStateLog)
        assert saved_log.estado_anterior == AssetStatus.OPERATIONAL
        assert saved_log.estado_nuevo == AssetStatus.UNDER_MAINTENANCE
        assert saved_log.usuario_id == uuid.UUID(user_id)

    async def test_update_asset_no_state_change_does_not_save_log(self, mock_uow: Any) -> None:
        # Arrange
        company_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())

        asset = Asset.create(
            empresa_id=CompanyId.from_string(company_id),
            articulo_id=uuid.uuid4(),
            ubicacion_id=None,
            serial_interno="SERIAL-333",
            codigo_activo="CODE-333",
            estado=AssetStatus.OPERATIONAL,
        )
        mock_uow.assets.get_by_id.return_value = asset

        request = UpdateAssetRequest(
            serial_interno="SERIAL-333-NEW",
            codigo_activo=None,
            estado=None,
            ubicacion_id=None,
            fecha_adquisicion=None,
            valor_monetario=None,
            moneda=None,
        )

        use_case = UpdateAssetUseCase(uow=mock_uow)

        # Act
        await use_case.execute(company_id, asset_id, request)

        # Assert
        assert mock_uow.assets.save.called
        assert not mock_uow.asset_state_logs.save.called
        assert mock_uow.commit.called
