"""Tests para casos de uso de planes de mantenimiento (CRUD)."""
from datetime import UTC, date, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.entities.maintenance_plan import MaintenancePlan
from app.domain.enums import MaintenanceType


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.maintenance_plans = MagicMock()
    uow.maintenance_plans.save = AsyncMock()
    uow.maintenance_plans.get_by_id = AsyncMock()
    uow.maintenance_plans.get_all_by_company = AsyncMock()
    uow.maintenance_plans.update = AsyncMock()
    uow.maintenance_plans.delete = AsyncMock()
    uow.plan_executions = MagicMock()
    uow.plan_executions.list_by_plan_id = AsyncMock(return_value=[])
    uow.commit = AsyncMock()
    return uow


def _make_plan(**overrides: Any) -> MaintenancePlan:
    defaults = {
        "id": uuid4(),
        "empresa_id": uuid4(),
        "activo_id": uuid4(),
        "nombre": "Mantenimiento Preventivo Q1",
        "tipo": MaintenanceType.PREVENTIVE,
        "intervalo_dias": 90,
        "proxima_ejecucion": date(2026, 9, 30),
        "tecnico_responsable_id": None,
        "descripcion_tareas": None,
        "activo": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return MaintenancePlan(**defaults)


class TestCreateMaintenancePlan:

    async def test_creates_plan_and_saves(self, mock_uow: Any) -> None:
        from app.application.dtos.maintenance_plan_dtos import (
            CreateMaintenancePlanRequest,
        )
        from app.application.use_cases.maintenance_plan.create_maintenance_plan import (
            CreateMaintenancePlanUseCase,
        )

        empresa_id = str(uuid4())
        activo_id = str(uuid4())
        request = CreateMaintenancePlanRequest(
            activo_id=activo_id,
            nombre="Mantenimiento Q1",
            tipo="preventivo",
            intervalo_dias=90,
            proxima_ejecucion=date(2026, 9, 30),
        )

        saved_plan = _make_plan(
            empresa_id=empresa_id,
            activo_id=activo_id,
            nombre="Mantenimiento Q1",
            tipo=MaintenanceType.PREVENTIVE,
            intervalo_dias=90,
            proxima_ejecucion=date(2026, 9, 30),
        )
        mock_uow.maintenance_plans.save.return_value = saved_plan

        use_case = CreateMaintenancePlanUseCase(uow=mock_uow)
        result = await use_case.execute(empresa_id, request)

        assert mock_uow.maintenance_plans.save.called
        assert result.nombre == "Mantenimiento Q1"
        assert result.tipo == "preventivo"

    async def test_creates_with_technician(self, mock_uow: Any) -> None:
        from app.application.dtos.maintenance_plan_dtos import (
            CreateMaintenancePlanRequest,
        )
        from app.application.use_cases.maintenance_plan.create_maintenance_plan import (
            CreateMaintenancePlanUseCase,
        )

        empresa_id = str(uuid4())
        tecnico_id = str(uuid4())
        mock_uow.maintenance_plans.save.return_value = _make_plan(
            empresa_id=empresa_id, tecnico_responsable_id=tecnico_id
        )

        use_case = CreateMaintenancePlanUseCase(uow=mock_uow)
        request = CreateMaintenancePlanRequest(
            activo_id=str(uuid4()),
            nombre="Plan con técnico",
            tipo="correctivo",
            intervalo_dias=30,
            proxima_ejecucion=date(2026, 7, 15),
            tecnico_responsable_id=tecnico_id,
        )

        result = await use_case.execute(empresa_id, request)

        assert result.tecnico_responsable_id == tecnico_id


class TestGetMaintenancePlan:

    async def test_returns_plan_when_found(self, mock_uow: Any) -> None:
        from app.application.use_cases.maintenance_plan.get_maintenance_plan import (
            GetMaintenancePlanUseCase,
        )

        plan_id = str(uuid4())
        empresa_id = str(uuid4())
        mock_uow.maintenance_plans.get_by_id.return_value = _make_plan(
            id=plan_id, empresa_id=empresa_id
        )

        use_case = GetMaintenancePlanUseCase(uow=mock_uow)
        result = await use_case.execute(empresa_id, plan_id)

        assert result.id == plan_id

    async def test_raises_not_found(self, mock_uow: Any) -> None:
        from app.application.use_cases.maintenance_plan.get_maintenance_plan import (
            GetMaintenancePlanUseCase,
        )
        from app.domain.exceptions.maintenance_plan import (
            MaintenancePlanNotFoundError,
        )

        mock_uow.maintenance_plans.get_by_id.return_value = None

        use_case = GetMaintenancePlanUseCase(uow=mock_uow)
        with pytest.raises(MaintenancePlanNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()))


class TestListMaintenancePlans:

    async def test_returns_paginated_plans(self, mock_uow: Any) -> None:
        from app.application.use_cases.maintenance_plan.list_maintenance_plan import (
            ListMaintenancePlansUseCase,
        )

        empresa_id = str(uuid4())
        plans = [_make_plan() for _ in range(3)]
        mock_uow.maintenance_plans.get_all_by_company.return_value = (plans, 3)

        use_case = ListMaintenancePlansUseCase(uow=mock_uow)
        result, total = await use_case.execute(empresa_id)

        assert total == 3
        assert len(result) == 3

    async def test_passes_filters_downstream(self, mock_uow: Any) -> None:
        from app.application.use_cases.maintenance_plan.list_maintenance_plan import (
            ListMaintenancePlansUseCase,
        )

        empresa_id = str(uuid4())
        mock_uow.maintenance_plans.get_all_by_company.return_value = ([], 0)

        use_case = ListMaintenancePlansUseCase(uow=mock_uow)
        filters = {"tipo": "preventivo", "activo": True}
        await use_case.execute(empresa_id, filters=filters)

        mock_uow.maintenance_plans.get_all_by_company.assert_called_once()
        args = mock_uow.maintenance_plans.get_all_by_company.call_args.args
        assert args[3] == filters  # 4th positional arg is filters


class TestUpdateMaintenancePlan:

    async def test_updates_fields(self, mock_uow: Any) -> None:
        from app.application.dtos.maintenance_plan_dtos import (
            UpdateMaintenancePlanRequest,
        )
        from app.application.use_cases.maintenance_plan.update_maintenance_plan import (
            UpdateMaintenancePlanUseCase,
        )

        empresa_id = str(uuid4())
        plan_id = str(uuid4())
        plan = _make_plan(id=plan_id, empresa_id=empresa_id, nombre="Old Name")
        mock_uow.maintenance_plans.get_by_id.return_value = plan
        mock_uow.maintenance_plans.update.return_value = _make_plan(
            id=plan_id, empresa_id=empresa_id, nombre="New Name"
        )

        use_case = UpdateMaintenancePlanUseCase(uow=mock_uow)
        request = UpdateMaintenancePlanRequest(
            nombre="New Name",
            _fields_set=frozenset(["nombre"]),
        )

        result = await use_case.execute(empresa_id, plan_id, request)

        assert result.nombre == "New Name"

    async def test_raises_not_found(self, mock_uow: Any) -> None:
        from app.application.dtos.maintenance_plan_dtos import (
            UpdateMaintenancePlanRequest,
        )
        from app.application.use_cases.maintenance_plan.update_maintenance_plan import (
            UpdateMaintenancePlanUseCase,
        )
        from app.domain.exceptions.maintenance_plan import (
            MaintenancePlanNotFoundError,
        )

        mock_uow.maintenance_plans.get_by_id.return_value = None

        use_case = UpdateMaintenancePlanUseCase(uow=mock_uow)
        request = UpdateMaintenancePlanRequest(
            nombre="New Name",
            _fields_set=frozenset(["nombre"]),
        )

        with pytest.raises(MaintenancePlanNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()), request)


class TestDeleteMaintenancePlan:

    async def test_deletes_when_found(self, mock_uow: Any) -> None:
        from app.application.use_cases.maintenance_plan.delete_maintenance_plan import (
            DeleteMaintenancePlanUseCase,
        )

        empresa_id = str(uuid4())
        plan_id = str(uuid4())
        mock_uow.maintenance_plans.get_by_id.return_value = _make_plan(
            id=plan_id, empresa_id=empresa_id
        )

        use_case = DeleteMaintenancePlanUseCase(uow=mock_uow)
        await use_case.execute(empresa_id, plan_id)

        mock_uow.maintenance_plans.delete.assert_called_once()

    async def test_raises_not_found(self, mock_uow: Any) -> None:
        from app.application.use_cases.maintenance_plan.delete_maintenance_plan import (
            DeleteMaintenancePlanUseCase,
        )
        from app.domain.exceptions.maintenance_plan import (
            MaintenancePlanNotFoundError,
        )

        mock_uow.maintenance_plans.get_by_id.return_value = None

        use_case = DeleteMaintenancePlanUseCase(uow=mock_uow)
        with pytest.raises(MaintenancePlanNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()))
