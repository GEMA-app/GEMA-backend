"""Tests para seguridad de endpoints de planes de mantenimiento."""
import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.maintenance_plans import (
    create_maintenance_plan,
    delete_maintenance_plan,
    get_maintenance_plan,
    list_maintenance_plans,
    update_maintenance_plan,
)


def _has_dependency(func: Callable[..., Any], param_name: str) -> bool:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    return hasattr(default, "dependency") and default.dependency is not None


class TestCreateEndpoint:

    def test_has_auth_dependency(self) -> None:
        assert _has_dependency(create_maintenance_plan, "current_user")

    def test_has_empresa_id_param(self) -> None:
        assert "empresa_id" in inspect.signature(create_maintenance_plan).parameters


class TestListEndpoint:

    def test_has_auth_dependency(self) -> None:
        assert _has_dependency(list_maintenance_plans, "current_user")

    def test_has_filter_params(self) -> None:
        sig = inspect.signature(list_maintenance_plans)
        assert "activo_id" in sig.parameters
        assert "tipo" in sig.parameters
        assert "activo" in sig.parameters

    def test_has_pagination_params(self) -> None:
        sig = inspect.signature(list_maintenance_plans)
        assert "offset" in sig.parameters
        assert "limit" in sig.parameters


class TestGetEndpoint:

    def test_has_auth_dependency(self) -> None:
        assert _has_dependency(get_maintenance_plan, "current_user")

    def test_uses_plan_id_param(self) -> None:
        assert "plan_id" in inspect.signature(get_maintenance_plan).parameters

    def test_uses_empresa_id_param(self) -> None:
        assert "empresa_id" in inspect.signature(get_maintenance_plan).parameters


class TestUpdateEndpoint:

    def test_has_auth_dependency(self) -> None:
        assert _has_dependency(update_maintenance_plan, "current_user")

    def test_uses_plan_id_param(self) -> None:
        assert "plan_id" in inspect.signature(update_maintenance_plan).parameters


class TestDeleteEndpoint:

    def test_has_auth_dependency(self) -> None:
        assert _has_dependency(delete_maintenance_plan, "current_user")

    def test_uses_plan_id_param(self) -> None:
        assert "plan_id" in inspect.signature(delete_maintenance_plan).parameters
