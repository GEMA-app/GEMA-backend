"""Tests unitarios para casos de uso de preferencias de usuario."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.use_cases.preference import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from app.domain.enums import Theme
from app.domain.exceptions.preference import PreferenceNotFoundError
from app.domain.value_objects import CompanyId, UserId


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.preferences = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def sample_pref():
    from app.domain.entities.preference import UserPreference
    pref = UserPreference(
        usuario_id=UserId(uuid4()),
        empresa_id=CompanyId(uuid4()),
        tema=Theme.LIGHT,
    )
    return pref


class TestGetUserPreferencesUseCase:
    async def test_get_preferences_success(self, mock_uow, sample_pref):
        mock_uow.preferences.get_by_user.return_value = sample_pref

        use_case = GetUserPreferencesUseCase(uow=mock_uow)
        result = await use_case.execute(str(sample_pref.empresa_id), str(sample_pref.usuario_id))

        assert result.tema == "claro"
        assert result.usuario_id == str(sample_pref.usuario_id)

    async def test_get_preferences_not_found(self, mock_uow):
        mock_uow.preferences.get_by_user.return_value = None

        use_case = GetUserPreferencesUseCase(uow=mock_uow)
        with pytest.raises(PreferenceNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()))


class TestUpdateUserPreferencesUseCase:
    async def test_update_preferences_success(self, mock_uow, sample_pref):
        from app.application.dtos.preference_dtos import UpdatePreferenceRequest
        sample_pref.tema = Theme.DARK

        dto = UpdatePreferenceRequest(tema="oscuro", version=1)
        mock_uow.preferences.get_by_user.return_value = sample_pref
        mock_uow.preferences.save.return_value = None

        use_case = UpdateUserPreferencesUseCase(uow=mock_uow)
        result = await use_case.execute(str(sample_pref.empresa_id), str(sample_pref.usuario_id), dto)

        assert result.tema == "oscuro"
        mock_uow.preferences.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_update_preferences_creates_if_not_found(self, mock_uow):
        from app.application.dtos.preference_dtos import UpdatePreferenceRequest
        mock_uow.preferences.get_by_user.return_value = None
        mock_uow.preferences.save.return_value = None

        use_case = UpdateUserPreferencesUseCase(uow=mock_uow)
        result = await use_case.execute(str(uuid4()), str(uuid4()), UpdatePreferenceRequest(tema="oscuro", version=1))

        assert result.tema == "oscuro"
        mock_uow.preferences.save.assert_awaited_once()
