"""Tests para el manejador de IntegrityError (conflictos de unicidad)."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from sqlalchemy.exc import IntegrityError

from app.presentation.exception_handlers.integrity import (
    _extract_constraint_name,
    integrity_error_handler,
)


class TestExtractConstraintName:

    def test_extract_constraint_name_asyncpg_cause(self) -> None:
        orig = MagicMock()
        cause = MagicMock()
        cause.constraint_name = "uq_activos_empresa_codigo_activo_lower"
        orig.__cause__ = cause
        exc = IntegrityError("stmt", {"param": 1}, orig)
        result = _extract_constraint_name(exc)
        assert result == "uq_activos_empresa_codigo_activo_lower"

    def test_extract_constraint_name_string_fallback(self) -> None:
        orig = Exception(
            'duplicate key value violates unique constraint '
            '"uq_activos_empresa_serial_interno"'
        )
        exc = IntegrityError("stmt", {"param": 1}, orig)
        result = _extract_constraint_name(exc)
        assert result == "uq_activos_empresa_serial_interno"

    def test_extract_constraint_name_no_cause_and_no_match(self) -> None:
        orig = Exception("some other database error")
        exc = IntegrityError("stmt", {"param": 1}, orig)
        result = _extract_constraint_name(exc)
        assert result is None


class TestIntegrityHandler:

    @pytest.mark.asyncio
    async def test_integrity_handler_returns_409(self) -> None:
        request = AsyncMock(spec=Request)
        request.method = "POST"
        request.url = MagicMock()
        request.url.path = "/v1/empresas/123/activos"

        orig = MagicMock()
        cause = MagicMock()
        cause.constraint_name = "uq_activos_empresa_codigo_activo_lower"
        orig.__cause__ = cause
        exc = IntegrityError("stmt", {"param": 1}, orig)

        with patch(
            "app.presentation.exception_handlers.integrity.domain_exception_handler",
            new=AsyncMock(return_value=MagicMock(status_code=409)),
        ):
            response = await integrity_error_handler(request, exc)
            assert response.status_code == 409
