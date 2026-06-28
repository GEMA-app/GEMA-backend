"""Tests unitarios para la entidad WorkOrder (máquina de estados, factory, update_details)."""

from datetime import datetime

from app.domain.entities.work_order import WorkOrder
from app.domain.enums import MaintenanceType, WorkOrderStatus
from app.domain.exceptions.work_order import (
    WorkOrderInvalidDataError,
    WorkOrderInvalidStateError,
)
from app.domain.value_objects import AssetId, CompanyId, UserId, WorkOrderId


def _make_id() -> WorkOrderId:
    return WorkOrderId.from_string("00000000-0000-0000-0000-000000000001")


def _make_company_id() -> CompanyId:
    return CompanyId.from_string("00000000-0000-0000-0000-000000000002")


def _make_asset_id() -> AssetId:
    return AssetId.from_string("00000000-0000-0000-0000-000000000003")


class TestWorkOrderCreate:
    """Tests para el factory method WorkOrder.create()."""

    def test_create_minimal(self) -> None:
        wo = WorkOrder.create(
            work_order_id=_make_id(),
            empresa_id=_make_company_id(),
            codigo_ot="OT-2026-0001",
            activo_id=_make_asset_id(),
            tipo=MaintenanceType.CORRECTIVE,
        )
        assert wo.id == _make_id()
        assert wo.empresa_id == _make_company_id()
        assert wo.codigo_ot == "OT-2026-0001"
        assert wo.activo_id == _make_asset_id()
        assert wo.tipo == MaintenanceType.CORRECTIVE
        assert wo.estado == WorkOrderStatus.OPEN
        assert wo.moneda == "USD"
        assert wo.fecha_apertura is not None
        assert isinstance(wo.fecha_apertura, datetime)
        assert wo.supervisor_id is None
        assert wo.descripcion_trabajo is None
        assert wo.costo_estimado is None

    def test_create_with_all_fields(self) -> None:
        supervisor = UserId.from_string("00000000-0000-0000-0000-000000000004")
        wo = WorkOrder.create(
            work_order_id=_make_id(),
            empresa_id=_make_company_id(),
            codigo_ot="OT-2026-0002",
            activo_id=_make_asset_id(),
            tipo=MaintenanceType.PREVENTIVE,
            supervisor_id=supervisor,
            descripcion_trabajo="  Mantenimiento preventivo  ",
            costo_estimado=1500.00,
            moneda="EUR",
        )
        assert wo.supervisor_id == supervisor
        assert wo.descripcion_trabajo == "Mantenimiento preventivo"
        assert wo.costo_estimado == 1500.00
        assert wo.moneda == "EUR"

    def test_create_raises_on_empty_codigo_ot(self) -> None:
        import pytest

        with pytest.raises(WorkOrderInvalidDataError, match="no puede estar vacío"):
            WorkOrder.create(
                work_order_id=_make_id(),
                empresa_id=_make_company_id(),
                codigo_ot="",
                activo_id=_make_asset_id(),
                tipo=MaintenanceType.CORRECTIVE,
            )

    def test_create_raises_on_whitespace_codigo_ot(self) -> None:
        import pytest

        with pytest.raises(WorkOrderInvalidDataError, match="no puede estar vacío"):
            WorkOrder.create(
                work_order_id=_make_id(),
                empresa_id=_make_company_id(),
                codigo_ot="   ",
                activo_id=_make_asset_id(),
                tipo=MaintenanceType.CORRECTIVE,
            )

    def test_create_raises_on_negative_costo_estimado(self) -> None:
        import pytest

        with pytest.raises(WorkOrderInvalidDataError, match="no puede ser negativo"):
            WorkOrder.create(
                work_order_id=_make_id(),
                empresa_id=_make_company_id(),
                codigo_ot="OT-2026-0003",
                activo_id=_make_asset_id(),
                tipo=MaintenanceType.CORRECTIVE,
                costo_estimado=-100.00,
            )

    def test_create_zero_costo_estimado(self) -> None:
        wo = WorkOrder.create(
            work_order_id=_make_id(),
            empresa_id=_make_company_id(),
            codigo_ot="OT-2026-0004",
            activo_id=_make_asset_id(),
            tipo=MaintenanceType.CORRECTIVE,
            costo_estimado=0.00,
        )
        assert wo.costo_estimado == 0.00


class TestWorkOrderStateMachine:
    """Tests para la máquina de estados de WorkOrder."""

    def _make_open_wo(self) -> WorkOrder:
        return WorkOrder.create(
            work_order_id=_make_id(),
            empresa_id=_make_company_id(),
            codigo_ot="OT-2026-0001",
            activo_id=_make_asset_id(),
            tipo=MaintenanceType.CORRECTIVE,
        )

    def test_initial_state_is_open(self) -> None:
        wo = self._make_open_wo()
        assert wo.estado == WorkOrderStatus.OPEN

    def test_start_sets_in_progress_and_fecha_inicio(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        assert wo.estado == WorkOrderStatus.IN_PROGRESS
        assert wo.fecha_inicio_trabajo is not None

    def test_open_can_cancel(self) -> None:
        wo = self._make_open_wo()
        wo.cancel()
        assert wo.estado == WorkOrderStatus.CANCELLED

    def test_in_progress_can_pause(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        wo.pause()
        assert wo.estado == WorkOrderStatus.PAUSED

    def test_in_progress_can_close(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        wo.close()
        assert wo.estado == WorkOrderStatus.CLOSED
        assert wo.fecha_cierre is not None

    def test_in_progress_can_cancel(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        wo.cancel()
        assert wo.estado == WorkOrderStatus.CANCELLED

    def test_paused_can_resume(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        wo.pause()
        wo.resume()
        assert wo.estado == WorkOrderStatus.IN_PROGRESS

    def test_paused_can_cancel(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        wo.pause()
        wo.cancel()
        assert wo.estado == WorkOrderStatus.CANCELLED

    def test_closed_cannot_transition(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        wo.close()
        import pytest

        with pytest.raises(WorkOrderInvalidStateError):
            wo.start()
        with pytest.raises(WorkOrderInvalidStateError):
            wo.pause()
        with pytest.raises(WorkOrderInvalidStateError):
            wo.resume()
        with pytest.raises(WorkOrderInvalidStateError):
            wo.cancel()

    def test_cancelled_cannot_transition(self) -> None:
        wo = self._make_open_wo()
        wo.cancel()
        import pytest

        with pytest.raises(WorkOrderInvalidStateError):
            wo.start()
        with pytest.raises(WorkOrderInvalidStateError):
            wo.pause()
        with pytest.raises(WorkOrderInvalidStateError):
            wo.close()

    def test_open_cannot_close_directly(self) -> None:
        wo = self._make_open_wo()
        import pytest

        with pytest.raises(WorkOrderInvalidStateError):
            wo.close()

    def test_open_cannot_pause_directly(self) -> None:
        wo = self._make_open_wo()
        import pytest

        with pytest.raises(WorkOrderInvalidStateError):
            wo.pause()

    def test_start_twice_raises(self) -> None:
        wo = self._make_open_wo()
        wo.start()
        import pytest

        with pytest.raises(WorkOrderInvalidStateError):
            wo.start()

    def test_full_lifecycle(self) -> None:
        wo = self._make_open_wo()
        assert wo.estado == WorkOrderStatus.OPEN

        wo.start()
        assert wo.estado == WorkOrderStatus.IN_PROGRESS  # type: ignore[comparison-overlap]
        assert wo.fecha_inicio_trabajo is not None

        wo.pause()
        assert wo.estado == WorkOrderStatus.PAUSED

        wo.resume()
        assert wo.estado == WorkOrderStatus.IN_PROGRESS

        wo.close()
        assert wo.estado == WorkOrderStatus.CLOSED
        assert wo.fecha_cierre is not None


class TestWorkOrderUpdateDetails:
    """Tests para WorkOrder.update_details()."""

    def _make_wo(self) -> WorkOrder:
        return WorkOrder.create(
            work_order_id=_make_id(),
            empresa_id=_make_company_id(),
            codigo_ot="OT-2026-0001",
            activo_id=_make_asset_id(),
            tipo=MaintenanceType.CORRECTIVE,
        )

    def test_update_all_fields(self) -> None:
        wo = self._make_wo()
        supervisor = UserId.from_string("00000000-0000-0000-0000-000000000004")
        wo.update_details(
            descripcion_trabajo="  Nueva descripción  ",
            costo_estimado=2000.00,
            costo_real=1800.00,
            supervisor_id=supervisor,
        )
        assert wo.descripcion_trabajo == "Nueva descripción"
        assert wo.costo_estimado == 2000.00
        assert wo.costo_real == 1800.00
        assert wo.supervisor_id == supervisor

    def test_update_partial(self) -> None:
        wo = self._make_wo()
        wo.update_details(costo_estimado=500.00)
        assert wo.costo_estimado == 500.00
        assert wo.descripcion_trabajo is None

    def test_negative_costo_estimado_raises(self) -> None:
        wo = self._make_wo()
        import pytest

        with pytest.raises(WorkOrderInvalidDataError, match="no puede ser negativo"):
            wo.update_details(costo_estimado=-1)

    def test_negative_costo_real_raises(self) -> None:
        wo = self._make_wo()
        import pytest

        with pytest.raises(WorkOrderInvalidDataError, match="no puede ser negativo"):
            wo.update_details(costo_real=-1)

    def test_zero_costs_allowed(self) -> None:
        wo = self._make_wo()
        wo.update_details(costo_estimado=0.00, costo_real=0.00)
        assert wo.costo_estimado == 0.00
        assert wo.costo_real == 0.00

    def test_none_fields_do_not_overwrite(self) -> None:
        wo = self._make_wo()
        wo.update_details(descripcion_trabajo="Trabajo inicial")
        wo.update_details(costo_estimado=None)
        assert wo.descripcion_trabajo == "Trabajo inicial"
        assert wo.costo_estimado is None


class TestWorkOrderGenerateCode:
    """Tests para WorkOrder.generate_code()."""

    def test_generate_code_format(self) -> None:
        company_id = _make_company_id()
        code = WorkOrder.generate_code(company_id)
        assert code.startswith("OT-")
        parts = code.split("-")
        assert len(parts) == 3
        assert parts[1].isdigit()  # año
        assert len(parts[2]) == 4  # hash padding

    def test_same_company_generates_same_code(self) -> None:
        company_id = _make_company_id()
        code1 = WorkOrder.generate_code(company_id)
        code2 = WorkOrder.generate_code(company_id)
        assert code1 == code2  # hash es determinista
