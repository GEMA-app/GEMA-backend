"""Tests unitarios para casos de uso de ejecuciones de plan de mantenimiento."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.plan_execution_dtos import PlanExecutionCreateRequest
from app.application.use_cases.plan_execution import (
    CreatePlanExecutionUseCase,
    GetPlanExecutionUseCase,
    ListPlanExecutionUseCase,
)
from app.domain.entities.plan_execution import PlanExecution
from app.domain.exceptions.plan_execution import PlanExecutionNotFoundError
from app.domain.value_objects import CompanyId


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.plan_executions = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


def _make_execution(plan_id=None, work_order_id=None):
    return PlanExecution.create(
        empresa_id=CompanyId(uuid4()),
        plan_id=plan_id or uuid4(),
        work_order_id=work_order_id or uuid4(),
        execution_date="2026-06-15",
        observations="Test",
    )


class TestCreatePlanExecutionUseCase:
    async def test_create_plan_execution_success(self, mock_uow):
        plan_id = uuid4()
        work_order_id = uuid4()
        dto = PlanExecutionCreateRequest(
            plan_id=plan_id,
            work_order_id=work_order_id,
            execution_date="2026-06-15",
            observations="Ejecución de prueba",
        )
        saved = _make_execution(plan_id=plan_id, work_order_id=work_order_id)
        mock_uow.plan_executions.save.return_value = saved

        use_case = CreatePlanExecutionUseCase(uow=mock_uow)
        result = await use_case.execute(str(uuid4()), dto)

        assert result.work_order_id == str(work_order_id)
        mock_uow.plan_executions.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_create_plan_execution_minimal(self, mock_uow):
        dto = PlanExecutionCreateRequest(
            plan_id=uuid4(),
            work_order_id=uuid4(),
            execution_date="2026-06-15",
            observations=None,
        )
        saved = _make_execution()
        mock_uow.plan_executions.save.return_value = saved

        use_case = CreatePlanExecutionUseCase(uow=mock_uow)
        result = await use_case.execute(str(uuid4()), dto)

        assert result is not None


class TestListPlanExecutionUseCase:
    async def test_list_plan_executions(self, mock_uow):
        company_id = uuid4()
        plan_id = uuid4()
        execution = PlanExecution.create(
            empresa_id=CompanyId(company_id),
            plan_id=plan_id,
            work_order_id=uuid4(),
            execution_date="2026-06-15",
            observations="Test",
        )
        mock_uow.plan_executions.list_by_plan_id.return_value = [execution]

        use_case = ListPlanExecutionUseCase(uow=mock_uow)
        result = await use_case.execute(str(company_id), str(plan_id))

        assert len(result.data) == 1

    async def test_list_plan_executions_empty(self, mock_uow):
        mock_uow.plan_executions.list_by_plan_id.return_value = []

        use_case = ListPlanExecutionUseCase(uow=mock_uow)
        result = await use_case.execute(str(uuid4()), str(uuid4()))

        assert len(result.data) == 0


class TestGetPlanExecutionUseCase:
    async def test_get_plan_execution_success(self, mock_uow):
        execution = _make_execution()
        mock_uow.plan_executions.get_by_id.return_value = execution

        use_case = GetPlanExecutionUseCase(uow=mock_uow)
        result = await use_case.execute(str(execution.empresa_id), str(execution.id))

        assert result.id == str(execution.id)

    async def test_get_plan_execution_not_found(self, mock_uow):
        mock_uow.plan_executions.get_by_id.return_value = None

        use_case = GetPlanExecutionUseCase(uow=mock_uow)
        with pytest.raises(PlanExecutionNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()))
