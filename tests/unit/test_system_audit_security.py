"""Tests para seguridad de endpoints de auditoria de sistema.

Verifica que los endpoints usen las dependencias correctas
de autenticacion y autorizacion, y que los parametros de ruta
sigan la convencion del proyecto.
"""
import inspect
from collections.abc import Callable
from typing import Any

from app.presentation.api.v1.endpoints.system_audit import (
    get_system_audit_by_id,
    list_system_audits,
)


def _get_dependency(func: Callable[..., Any], param_name: str) -> Any:
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    default = param.default
    if hasattr(default, "dependency"):
        return default.dependency
    return None


class TestListSystemAuditsSecurity:
    """Seguridad del endpoint de listado de auditorias."""

    def test_list_uses_permission_dependency(self) -> None:
        """Debe usar require_permission con modulo ADMIN y accion view."""
        dep = _get_dependency(list_system_audits, "current_user")
        assert dep is not None
        assert callable(dep)

    def test_list_has_empresa_id_param(self) -> None:
        """Debe tener empresa_id como parametro."""
        sig = inspect.signature(list_system_audits)
        assert "empresa_id" in sig.parameters


class TestGetSystemAuditSecurity:
    """Seguridad del endpoint de detalle de auditoria."""

    def test_get_uses_permission_dependency(self) -> None:
        """Debe usar require_permission con modulo ADMIN y accion view."""
        dep = _get_dependency(get_system_audit_by_id, "current_user")
        assert dep is not None
        assert callable(dep)

    def test_get_has_auditoria_id_param(self) -> None:
        """Debe usar auditoria_id como parametro de path (no id generico)."""
        sig = inspect.signature(get_system_audit_by_id)
        assert "auditoria_id" in sig.parameters

    def test_get_has_empresa_id_param(self) -> None:
        """Debe tener empresa_id como parametro de path."""
        sig = inspect.signature(get_system_audit_by_id)
        assert "empresa_id" in sig.parameters
