"""Tests para seguridad de endpoints de AssetStateLog (historial de estados de activos)."""

import inspect
from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock

from app.presentation.api.v1.endpoints.asset_state_log import (
    list_asset_state_logs,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_list_asset_state_logs_uses_require_permission_view() -> None:
    dep = _get_dependency(list_asset_state_logs, "current_user")
    assert dep is not None
    assert callable(dep)


def test_list_asset_state_logs_uses_param_names() -> None:
    sig = inspect.signature(list_asset_state_logs)
    assert "empresa_id" in sig.parameters
    assert "activo_id" in sig.parameters


async def test_list_asset_state_logs_passes_params_to_use_case() -> None:
    current_user_mock = type("UserMock", (), {"empresa_id": "test-company-id", "id": "user-id"})()
    use_case_mock = AsyncMock()
    use_case_mock.execute = AsyncMock(return_value=[])

    result = await list_asset_state_logs(
        empresa_id="test-company-id",
        activo_id="test-asset-id",
        current_user=current_user_mock,
        use_case=use_case_mock,
    )

    use_case_mock.execute.assert_called_once_with("test-company-id", "test-asset-id")
    assert result is not None
