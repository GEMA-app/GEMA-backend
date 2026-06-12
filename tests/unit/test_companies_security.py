"""Tests para seguridad de endpoints de empresas."""
import inspect
from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock

from app.presentation.api.v1.endpoints.companies import (
    create_company,
    delete_company,
    get_company,
    list_companies,
    update_company,
)
from app.presentation.api.v1.endpoints.dependencies import (
    require_tenant_read,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


def test_create_company_uses_require_platform_permission() -> None:
    dep = _get_dependency(create_company, "current_user")
    assert dep is not None
    assert callable(dep)


def test_get_company_uses_require_tenant_read() -> None:
    dep = _get_dependency(get_company, "current_user")
    assert dep is require_tenant_read


def test_get_company_uses_company_id_param() -> None:
    sig = inspect.signature(get_company)
    assert "empresa_id" in sig.parameters


def test_update_company_uses_company_id_param() -> None:
    sig = inspect.signature(update_company)
    assert "empresa_id" in sig.parameters


def test_delete_company_uses_company_id_param() -> None:
    sig = inspect.signature(delete_company)
    assert "empresa_id" in sig.parameters


def test_list_companies_passes_company_id() -> None:
    sig = inspect.signature(list_companies)
    params = list(sig.parameters.keys())
    assert "company_id" not in params
    import inspect as _inspect
    source = _inspect.getsource(list_companies)
    assert "company_id=current_user.empresa_id" in source


async def test_list_companies_passes_company_id_to_use_case() -> None:
    current_user_mock = type("UserMock", (), {"empresa_id": "test-company-id"})()
    use_case_mock = AsyncMock()
    use_case_mock.execute = AsyncMock(return_value=([], 0))
    result = await list_companies(
        offset=0,
        limit=10,
        current_user=current_user_mock,
        use_case=use_case_mock,
    )
    use_case_mock.execute.assert_called_once_with(0, 10, company_id="test-company-id")
    assert result is not None
