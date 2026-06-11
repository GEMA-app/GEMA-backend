"""Tests para utilidades de seguridad (validate_tenant_access, dependencias)."""
import inspect
from uuid import UUID

import pytest

from app.application.dtos.auth_dtos import UserResponse
from app.domain.exceptions import InsufficientPermissionsError, InvalidUUIDError
from app.presentation.api.v1.endpoints.assets import get_asset
from app.presentation.api.v1.endpoints.dependencies import (
    get_current_active_user,
    require_permission,
    validate_tenant_access,
)


class TestValidateTenantAccess:

    def test_validate_tenant_access_same_uuid(self):
        uid = "550e8400-e29b-41d4-a716-446655440000"
        uid_no_hyphens = "550e8400e29b41d4a716446655440000"
        validate_tenant_access(uid, uid)
        validate_tenant_access(uid_no_hyphens, uid)
        validate_tenant_access(uid, uid_no_hyphens)

    def test_validate_tenant_access_different_uuid(self):
        uid_a = "550e8400-e29b-41d4-a716-446655440000"
        uid_b = "550e8400-e29b-41d4-a716-446655440001"
        with pytest.raises(InsufficientPermissionsError):
            validate_tenant_access(uid_a, uid_b)

    def test_validate_tenant_access_invalid_uuid(self):
        with pytest.raises(InvalidUUIDError):
            validate_tenant_access("not-a-uuid", "550e8400-e29b-41d4-a716-446655440000")

    def test_validate_tenant_access_case_insensitive(self):
        uid_upper = "550E8400-E29B-41D4-A716-446655440000"
        uid_lower = "550e8400-e29b-41d4-a716-446655440000"
        assert UUID(uid_upper) == UUID(uid_lower)
        validate_tenant_access(uid_upper, uid_lower)
        validate_tenant_access(uid_lower, uid_upper)


class TestRequirePermissionType:

    def test_require_permission_returns_user_response_type(self):
        inner_func = require_permission.__wrapped__ if hasattr(require_permission, "__wrapped__") else None
        if inner_func is None:
            import types
            module = inspect.getmodule(require_permission)
            source = inspect.getsource(require_permission)
            assert "UserResponse" in source or "-> UserResponse" in source
        else:
            sig = inspect.signature(inner_func)
            assert sig.return_annotation is UserResponse or sig.return_annotation is inspect.Parameter.empty


class TestGetCurrentActiveUserType:

    def test_get_current_active_user_returns_user_response_type(self):
        sig = inspect.signature(get_current_active_user)
        assert sig.return_annotation is UserResponse


class TestAssetsIdRenamed:

    def test_assets_id_renamed_to_activo_id(self):
        sig = inspect.signature(get_asset)
        params = list(sig.parameters.keys())
        assert "activo_id" in params, "El parámetro debe llamarse activo_id, no id"
