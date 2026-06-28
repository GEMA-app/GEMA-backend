"""Tests unitarios para los casos de uso de auditoria de sistema.

Cubre los casos de uso GetSystemAuditUseCase y ListSystemAuditsUseCase
usando mocks del UoW para evitar dependencias de infraestructura.
"""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.system_audit_dtos import (
    ListSystemAuditsRequest,
    SystemAuditResponse,
)
from app.application.use_cases.system_audit.get_system_audit import GetSystemAuditUseCase
from app.application.use_cases.system_audit.list_system_audits import ListSystemAuditsUseCase
from app.domain.exceptions.system_audit import SystemAuditNotFoundError

# ---------------------------------------------------------------------------
# Fixtures compartidos
# ---------------------------------------------------------------------------


@pytest.fixture
def company_id_str() -> str:
    """UUID de empresa/tenant valido."""
    return str(uuid4())


@pytest.fixture
def mock_audit_entity(company_id_str: str) -> Any:
    """Mock de entidad de dominio SystemAudit."""
    entity = MagicMock()
    entity.id = uuid4()
    entity.empresa_id = MagicMock()
    entity.empresa_id.__str__ = lambda _: company_id_str
    entity.usuario_id = MagicMock()
    entity.usuario_id.__str__ = lambda _: str(uuid4())
    entity.accion = "user.login"
    entity.detalles = {"ip": "192.168.1.1"}
    entity.ip_address = "192.168.1.1"
    entity.ocurrido_en = datetime.now(UTC)
    return entity


@pytest.fixture
def mock_uow(mock_audit_entity: Any) -> Any:
    """Mock del Unit of Work con repositorio de auditorias configurado."""
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.system_audits = MagicMock()
    uow.system_audits.get_by_id = AsyncMock(return_value=mock_audit_entity)
    uow.system_audits.get_all_by_company = AsyncMock(return_value=([mock_audit_entity], 1))
    uow.commit = AsyncMock()
    return uow


# ---------------------------------------------------------------------------
# Tests: GetSystemAuditUseCase
# ---------------------------------------------------------------------------


class TestGetSystemAuditUseCase:
    """Tests del caso de uso para obtener una auditoria por ID."""

    async def test_execute_returns_dto_when_audit_exists(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """Debe retornar un SystemAuditResponse cuando la auditoria existe."""
        use_case = GetSystemAuditUseCase(uow=mock_uow)

        result = await use_case.execute(company_id_str=company_id_str, audit_id=mock_audit_entity.id)

        assert isinstance(result, SystemAuditResponse)
        assert result.id == str(mock_audit_entity.id)
        assert result.accion == "user.login"

    async def test_execute_calls_repository_with_correct_params(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe llamar al repositorio con company_id y audit_id correctos."""
        use_case = GetSystemAuditUseCase(uow=mock_uow)
        audit_id = uuid4()
        await use_case.execute(company_id_str=company_id_str, audit_id=audit_id)

        mock_uow.system_audits.get_by_id.assert_called_once()
        call_args = mock_uow.system_audits.get_by_id.call_args[0]
        assert call_args[1] == audit_id

    async def test_execute_raises_not_found_when_audit_missing(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe lanzar SystemAuditNotFoundError si la auditoria no existe."""
        mock_uow.system_audits.get_by_id.return_value = None
        use_case = GetSystemAuditUseCase(uow=mock_uow)
        audit_id = uuid4()
        with pytest.raises(SystemAuditNotFoundError):
            await use_case.execute(company_id_str=company_id_str, audit_id=audit_id)

    async def test_execute_uses_uow_context_manager(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """Debe usar el UoW como context manager asincrono."""
        use_case = GetSystemAuditUseCase(uow=mock_uow)

        await use_case.execute(company_id_str=company_id_str, audit_id=mock_audit_entity.id)

        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_execute_maps_all_dto_fields(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """Debe mapear todos los campos de la entidad al DTO de respuesta."""
        use_case = GetSystemAuditUseCase(uow=mock_uow)

        result = await use_case.execute(company_id_str=company_id_str, audit_id=mock_audit_entity.id)

        assert result.ip_address == mock_audit_entity.ip_address
        assert result.detalles == mock_audit_entity.detalles
        assert result.ocurrido_en == mock_audit_entity.ocurrido_en

    async def test_execute_handles_null_usuario_id(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """Debe manejar correctamente cuando usuario_id es None."""
        mock_audit_entity.usuario_id = None
        use_case = GetSystemAuditUseCase(uow=mock_uow)

        result = await use_case.execute(company_id_str=company_id_str, audit_id=mock_audit_entity.id)

        assert result.usuario_id is None

    async def test_execute_handles_null_ip_address(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """Debe manejar correctamente cuando ip_address es None."""
        mock_audit_entity.ip_address = None
        use_case = GetSystemAuditUseCase(uow=mock_uow)

        result = await use_case.execute(company_id_str=company_id_str, audit_id=mock_audit_entity.id)

        assert result.ip_address is None

    async def test_execute_does_not_call_commit(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """No debe llamar a commit (modulo read-only)."""
        use_case = GetSystemAuditUseCase(uow=mock_uow)

        await use_case.execute(company_id_str=company_id_str, audit_id=mock_audit_entity.id)

        mock_uow.commit.assert_not_called()



# ---------------------------------------------------------------------------
# Tests: ListSystemAuditsUseCase
# ---------------------------------------------------------------------------


class TestListSystemAuditsUseCase:
    """Tests del caso de uso para listar auditorias del sistema."""

    async def test_execute_returns_list_and_total(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe retornar una tupla (lista de DTOs, total)."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        dtos, total = await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        assert isinstance(dtos, list)
        assert len(dtos) == 1
        assert total == 1

    async def test_execute_returns_empty_list_when_no_audits(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe retornar lista vacia y total 0 si no hay auditorias."""
        mock_uow.system_audits.get_all_by_company.return_value = ([], 0)
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        dtos, total = await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        assert dtos == []
        assert total == 0

    async def test_execute_passes_offset_and_limit_to_repo(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe pasar offset y limit correctamente al repositorio."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        await use_case.execute(
            company_id_str=company_id_str, offset=10, limit=5, request=request
        )

        call_args = mock_uow.system_audits.get_all_by_company.call_args[0]
        assert call_args[1] == 10  # offset
        assert call_args[2] == 5   # limit

    async def test_execute_passes_usuario_id_filter(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe incluir el filtro usuario_id en el dict de filtros."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        uid = str(uuid4())
        request = ListSystemAuditsRequest(usuario_id=uid)

        await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        filters = mock_uow.system_audits.get_all_by_company.call_args[0][3]
        assert filters.get("usuario_id") == uid

    async def test_execute_passes_accion_filter(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe incluir el filtro accion en el dict de filtros."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest(accion="user.login")

        await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        filters = mock_uow.system_audits.get_all_by_company.call_args[0][3]
        assert filters.get("accion") == "user.login"

    async def test_execute_passes_date_filters(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe incluir los filtros de fecha inicio y fin si se proveen."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        fecha_inicio = datetime(2026, 1, 1, tzinfo=UTC)
        fecha_fin = datetime(2026, 12, 31, tzinfo=UTC)
        request = ListSystemAuditsRequest(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

        await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        filters = mock_uow.system_audits.get_all_by_company.call_args[0][3]
        assert filters.get("fecha_inicio") == fecha_inicio
        assert filters.get("fecha_fin") == fecha_fin

    async def test_execute_excludes_none_filters(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """No debe incluir filtros con valor None en el dict enviado al repo."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        filters = mock_uow.system_audits.get_all_by_company.call_args[0][3]
        assert "usuario_id" not in filters
        assert "accion" not in filters
        assert "fecha_inicio" not in filters
        assert "fecha_fin" not in filters

    async def test_execute_maps_entities_to_dtos(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """Debe mapear cada entidad a un SystemAuditResponse."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        dtos, _ = await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        assert all(isinstance(d, SystemAuditResponse) for d in dtos)
        assert dtos[0].accion == mock_audit_entity.accion

    async def test_execute_uses_uow_context_manager(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """Debe usar el UoW como context manager asincrono."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_execute_does_not_call_commit(
        self, mock_uow: Any, company_id_str: str
    ) -> None:
        """No debe llamar a commit (modulo read-only)."""
        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=20, request=request
        )

        mock_uow.commit.assert_not_called()

    async def test_execute_multiple_audits(
        self, mock_uow: Any, company_id_str: str, mock_audit_entity: Any
    ) -> None:
        """Debe soportar respuestas con multiples entidades y total mayor."""
        entity2 = MagicMock()
        entity2.id = 2
        entity2.empresa_id = mock_audit_entity.empresa_id
        entity2.usuario_id = None
        entity2.accion = "asset.create"
        entity2.detalles = {}
        entity2.ip_address = None
        entity2.ocurrido_en = datetime.now(UTC)
        mock_uow.system_audits.get_all_by_company.return_value = (
            [mock_audit_entity, entity2],
            50,
        )

        use_case = ListSystemAuditsUseCase(uow=mock_uow)
        request = ListSystemAuditsRequest()

        dtos, total = await use_case.execute(
            company_id_str=company_id_str, offset=0, limit=2, request=request
        )

        assert len(dtos) == 2
        assert total == 50


# ---------------------------------------------------------------------------
# Tests: Entidad de Dominio SystemAudit
# ---------------------------------------------------------------------------


class TestSystemAuditEntity:
    """Tests de invariantes de la entidad de dominio SystemAudit."""

    def test_create_factory_sets_id_none(self) -> None:
        """El factory create() debe asignar id=None (autogenerado por BD)."""
        from app.domain.entities.system_audit import SystemAudit
        from app.domain.value_objects import CompanyId

        company_id = CompanyId(uuid4())
        audit = SystemAudit.create(
            empresa_id=company_id,
            usuario_id=None,
            accion="test.action",
        )

        assert audit.id is None

    def test_create_factory_sets_empty_detalles_by_default(self) -> None:
        """El factory create() debe asignar detalles={} si no se pasa."""
        from app.domain.entities.system_audit import SystemAudit
        from app.domain.value_objects import CompanyId

        company_id = CompanyId(uuid4())
        audit = SystemAudit.create(
            empresa_id=company_id,
            usuario_id=None,
            accion="test.action",
        )

        assert audit.detalles == {}

    def test_create_factory_preserves_detalles(self) -> None:
        """El factory create() debe conservar el dict de detalles provisto."""
        from app.domain.entities.system_audit import SystemAudit
        from app.domain.value_objects import CompanyId

        company_id = CompanyId(uuid4())
        payload = {"key": "value", "nested": {"a": 1}}
        audit = SystemAudit.create(
            empresa_id=company_id,
            usuario_id=None,
            accion="test.action",
            detalles=payload,
        )

        assert audit.detalles == payload

    def test_post_init_raises_on_empty_accion(self) -> None:
        """__post_init__ debe lanzar SystemAuditException si accion esta vacia."""
        from app.domain.entities.system_audit import SystemAudit
        from app.domain.exceptions.system_audit import SystemAuditException
        from app.domain.value_objects import CompanyId

        company_id = CompanyId(uuid4())

        with pytest.raises(SystemAuditException):
            SystemAudit(
                id=None,
                empresa_id=company_id,
                usuario_id=None,
                accion="   ",
                detalles={},
                ip_address=None,
                ocurrido_en=datetime.now(UTC),
            )

    def test_post_init_raises_on_none_empresa_id(self) -> None:
        """__post_init__ debe lanzar SystemAuditException si empresa_id es None."""
        from app.domain.entities.system_audit import SystemAudit
        from app.domain.exceptions.system_audit import SystemAuditException

        with pytest.raises(SystemAuditException):
            SystemAudit(
                id=None,
                empresa_id=None,  # type: ignore[arg-type]
                usuario_id=None,
                accion="valid.action",
                detalles={},
                ip_address=None,
                ocurrido_en=datetime.now(UTC),
            )

    def test_not_found_error_message_contains_ids(self) -> None:
        """SystemAuditNotFoundError debe contener audit_id y empresa_id en el mensaje."""
        from app.domain.exceptions.system_audit import SystemAuditNotFoundError

        cid = str(uuid4())
        err = SystemAuditNotFoundError(audit_id=99, empresa_id=cid)

        assert "99" in err.message
        assert cid in err.message
