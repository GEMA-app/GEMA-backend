"""Tests unitarios para los use cases de WorkOrder."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.work_order_dtos import (
    ChangeWorkOrderStatusRequest,
    CreateWorkOrderRequest,
    UpdateWorkOrderRequest,
)
from app.application.use_cases.work_order.assign_technician import (
    AssignTechnicianUseCase,
)
from app.application.use_cases.work_order.change_work_order_status import (
    ChangeWorkOrderStatusUseCase,
)
from app.application.use_cases.work_order.create_work_order import (
    CreateWorkOrderUseCase,
)
from app.application.use_cases.work_order.delete_work_order import (
    DeleteWorkOrderUseCase,
)
from app.application.use_cases.work_order.get_status_history import (
    GetWorkOrderStatusHistoryUseCase,
)
from app.application.use_cases.work_order.get_work_order import GetWorkOrderUseCase
from app.application.use_cases.work_order.list_work_order import (
    ListWorkOrdersUseCase,
)
from app.application.use_cases.work_order.remove_technician import (
    RemoveTechnicianUseCase,
)
from app.application.use_cases.work_order.update_work_order import (
    UpdateWorkOrderUseCase,
)
from app.application.use_cases.work_order.validate_work_order import (
    ValidateWorkOrderUseCase,
)
from app.domain.entities import WorkOrder
from app.domain.enums import MaintenanceType, WorkOrderStatus
from app.domain.exceptions import (
    AssetNotFoundError,
    WorkOrderCodeExistsError,
    WorkOrderInvalidStateError,
    WorkOrderNotFoundError,
)
from app.domain.value_objects import (
    AssetId,
    CompanyId,
    WorkOrderId,
)

UUID1 = "00000000-0000-0000-0000-000000000001"
UUID2 = "00000000-0000-0000-0000-000000000002"
UUID3 = "00000000-0000-0000-0000-000000000003"
UUID4 = "00000000-0000-0000-0000-000000000004"


def _make_wo(
    estado: WorkOrderStatus = WorkOrderStatus.OPEN,
) -> WorkOrder:
    return WorkOrder(
        id=WorkOrderId.from_string(UUID1),
        empresa_id=CompanyId.from_string(UUID2),
        codigo_ot="OT-2026-0001",
        activo_id=AssetId.from_string(UUID3),
        tipo=MaintenanceType.CORRECTIVE,
        estado=estado,
    )


def _mock_uow() -> MagicMock:
    uow = MagicMock()
    uow.work_orders = MagicMock()
    uow.work_orders.save = AsyncMock()
    uow.work_orders.get_by_id = AsyncMock()
    uow.work_orders.get_by_code = AsyncMock()
    uow.work_orders.list_by_company = AsyncMock()
    uow.work_orders.delete = AsyncMock()
    uow.work_orders.assign_technician = AsyncMock()
    uow.work_orders.remove_technician = AsyncMock()
    uow.work_orders.add_status_log = AsyncMock()
    uow.work_orders.get_status_history = AsyncMock()
    uow.assets = MagicMock()
    uow.assets.get_by_id = AsyncMock()
    uow.users = MagicMock()
    uow.users.get_by_id = AsyncMock()
    uow.commit = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


class TestCreateWorkOrderUseCase:
    async def test_create_ok(self) -> None:
        uow = _mock_uow()
        uow.assets.get_by_id.return_value = MagicMock()
        uow.work_orders.get_by_code.return_value = None
        use_case = CreateWorkOrderUseCase(uow)
        dto = CreateWorkOrderRequest(
            activo_id=UUID3,
            tipo="correctivo",
            descripcion_trabajo="Test",
        )
        result = await use_case.execute(UUID2, dto)

        assert result.codigo_ot is not None
        assert result.activo_id == UUID3
        assert result.estado == "abierta"
        uow.work_orders.save.assert_awaited_once()
        uow.commit.assert_awaited_once()

    async def test_create_raises_if_asset_not_found(self) -> None:
        uow = _mock_uow()
        uow.assets.get_by_id.return_value = None
        use_case = CreateWorkOrderUseCase(uow)
        dto = CreateWorkOrderRequest(activo_id=UUID3, tipo="correctivo")
        with pytest.raises(AssetNotFoundError):
            await use_case.execute(UUID2, dto)

    async def test_create_raises_if_code_exists(self) -> None:
        uow = _mock_uow()
        uow.assets.get_by_id.return_value = MagicMock()
        uow.work_orders.get_by_code.return_value = MagicMock()
        use_case = CreateWorkOrderUseCase(uow)
        dto = CreateWorkOrderRequest(
            activo_id=UUID3,
            tipo="correctivo",
            codigo_ot="OT-2026-0001",
        )
        with pytest.raises(WorkOrderCodeExistsError):
            await use_case.execute(UUID2, dto)

    async def test_create_with_explicit_code_and_supervisor(self) -> None:
        uow = _mock_uow()
        uow.assets.get_by_id.return_value = MagicMock()
        uow.work_orders.get_by_code.return_value = None
        use_case = CreateWorkOrderUseCase(uow)
        dto = CreateWorkOrderRequest(
            activo_id=UUID3,
            tipo="preventivo",
            codigo_ot="OT-2026-MANUAL",
            supervisor_id=UUID4,
            costo_estimado=500.00,
        )
        result = await use_case.execute(UUID2, dto)
        assert result.codigo_ot == "OT-2026-MANUAL"
        assert result.supervisor_id == UUID4
        assert result.costo_estimado == 500.00


class TestGetWorkOrderUseCase:
    async def test_get_ok(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo()
        use_case = GetWorkOrderUseCase(uow)
        result = await use_case.execute(UUID2, UUID1)
        assert result.id == UUID1
        assert result.codigo_ot == "OT-2026-0001"

    async def test_get_not_found(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = GetWorkOrderUseCase(uow)
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1)


class TestListWorkOrdersUseCase:
    async def test_list_returns_entities_and_count(self) -> None:
        uow = _mock_uow()
        wo = _make_wo()
        uow.work_orders.list_by_company.return_value = ([wo], 1)
        use_case = ListWorkOrdersUseCase(uow)
        results, total = await use_case.execute(UUID2)
        assert total == 1
        assert len(results) == 1
        assert results[0].id == UUID1

    async def test_list_empty(self) -> None:
        uow = _mock_uow()
        uow.work_orders.list_by_company.return_value = ([], 0)
        use_case = ListWorkOrdersUseCase(uow)
        results, total = await use_case.execute(UUID2)
        assert total == 0
        assert results == []

    async def test_list_with_filters(self) -> None:
        uow = _mock_uow()
        uow.work_orders.list_by_company.return_value = ([], 0)
        use_case = ListWorkOrdersUseCase(uow)
        await use_case.execute(UUID2, estado="abierta", activo_id=UUID3)
        uow.work_orders.list_by_company.assert_called_once()


class TestUpdateWorkOrderUseCase:
    async def test_update_ok(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo()
        use_case = UpdateWorkOrderUseCase(uow)
        dto = UpdateWorkOrderRequest(descripcion_trabajo="Actualizado")
        result = await use_case.execute(UUID2, UUID1, dto)
        assert result.descripcion_trabajo == "Actualizado"
        uow.work_orders.save.assert_awaited_once()
        uow.commit.assert_awaited_once()

    async def test_update_not_found(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = UpdateWorkOrderUseCase(uow)
        dto = UpdateWorkOrderRequest()
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1, dto)


class TestDeleteWorkOrderUseCase:
    async def test_delete_ok(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo()
        use_case = DeleteWorkOrderUseCase(uow)
        await use_case.execute(UUID2, UUID1)
        uow.work_orders.delete.assert_awaited_once()
        uow.commit.assert_awaited_once()

    async def test_delete_not_found(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = DeleteWorkOrderUseCase(uow)
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1)


class TestChangeWorkOrderStatusUseCase:
    async def test_start_work_order(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo(WorkOrderStatus.OPEN)
        use_case = ChangeWorkOrderStatusUseCase(uow)
        dto = ChangeWorkOrderStatusRequest(estado="en_proceso")
        result = await use_case.execute(UUID2, UUID1, dto)
        assert result.estado == "en_proceso"

    async def test_close_work_order(self) -> None:
        uow = _mock_uow()
        wo = _make_wo(WorkOrderStatus.IN_PROGRESS)
        uow.work_orders.get_by_id.return_value = wo
        use_case = ChangeWorkOrderStatusUseCase(uow)
        dto = ChangeWorkOrderStatusRequest(estado="cerrada")
        result = await use_case.execute(UUID2, UUID1, dto)
        assert result.estado == "cerrada"

    async def test_invalid_transition_raises(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo(WorkOrderStatus.OPEN)
        use_case = ChangeWorkOrderStatusUseCase(uow)
        dto = ChangeWorkOrderStatusRequest(estado="cerrada")
        with pytest.raises(WorkOrderInvalidStateError):
            await use_case.execute(UUID2, UUID1, dto)

    async def test_not_found_raises(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = ChangeWorkOrderStatusUseCase(uow)
        dto = ChangeWorkOrderStatusRequest(estado="en_proceso")
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1, dto)


class TestAssignTechnicianUseCase:
    async def test_assign_technician_ok(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo()
        user_mock = MagicMock()
        user_mock.empresa_id = UUID2
        uow.users.get_by_id.return_value = user_mock

        use_case = AssignTechnicianUseCase(uow)
        await use_case.execute(UUID2, UUID1, UUID4)
        uow.commit.assert_awaited_once()

    async def test_assign_technician_work_order_not_found(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = AssignTechnicianUseCase(uow)
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1, UUID4)

    async def test_assign_technician_user_not_found_or_different_company(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo()
        uow.users.get_by_id.return_value = None
        use_case = AssignTechnicianUseCase(uow)
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1, UUID4)


class TestRemoveTechnicianUseCase:
    async def test_remove_technician_ok(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo()
        use_case = RemoveTechnicianUseCase(uow)
        await use_case.execute(UUID2, UUID1, UUID4)
        uow.commit.assert_awaited_once()

    async def test_remove_technician_work_order_not_found(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = RemoveTechnicianUseCase(uow)
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1, UUID4)


class TestValidateWorkOrderUseCase:
    async def test_validate_work_order_ok(self) -> None:
        uow = _mock_uow()
        wo = _make_wo(WorkOrderStatus.CLOSED)
        uow.work_orders.get_by_id.return_value = wo
        use_case = ValidateWorkOrderUseCase(uow)
        result = await use_case.execute(UUID2, UUID1, UUID4)
        assert result.validado_por_id == UUID4
        assert result.fecha_validacion is not None
        uow.work_orders.save.assert_awaited_once()
        uow.commit.assert_awaited_once()

    async def test_validate_work_order_not_found(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = ValidateWorkOrderUseCase(uow)
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1, UUID4)


class TestGetWorkOrderStatusHistoryUseCase:
    async def test_get_history_ok(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = _make_wo()
        uow.work_orders.get_status_history.return_value = []
        use_case = GetWorkOrderStatusHistoryUseCase(uow)
        result = await use_case.execute(UUID2, UUID1)
        assert isinstance(result, list)

    async def test_get_history_work_order_not_found(self) -> None:
        uow = _mock_uow()
        uow.work_orders.get_by_id.return_value = None
        use_case = GetWorkOrderStatusHistoryUseCase(uow)
        with pytest.raises(WorkOrderNotFoundError):
            await use_case.execute(UUID2, UUID1)
