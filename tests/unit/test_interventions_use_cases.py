"""Tests for technical interventions use cases."""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dtos.intervention_dtos import (
    CreateInterventionRequest,
    UpdateInterventionRequest,
)
from app.application.use_cases.intervention.create_intervention import CreateInterventionUseCase
from app.application.use_cases.intervention.get_intervention import GetInterventionUseCase
from app.application.use_cases.intervention.list_interventions import ListInterventionsUseCase
from app.application.use_cases.intervention.update_intervention import UpdateInterventionUseCase
from app.domain.entities.intervention import TechnicalIntervention
from app.domain.exceptions.intervention import (
    InterventionNotFoundError,
)
from app.domain.value_objects.identifier import CompanyId, InterventionId, UserId, WorkOrderId


@pytest.fixture
def mock_repo() -> Any:
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_work_order = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_uow(mock_repo: Any) -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.interventions = mock_repo
    uow.used_parts = MagicMock()
    uow.used_parts.get_by_intervention = AsyncMock(return_value=[])
    uow.used_parts.get_by_work_order = AsyncMock(return_value=[])
    return uow


class TestCreateInterventionUseCase:

    async def test_create_intervention_successful(self, mock_uow: Any, mock_repo: Any) -> None:
        use_case = CreateInterventionUseCase(uow=mock_uow)
        empresa_id = str(uuid4())
        ot_id = str(uuid4())
        tecnico_id = uuid4()

        request = CreateInterventionRequest(
            technician_id=tecnico_id,
            tareas_realizadas="Reemplazo de filtro de aire",
            fecha_inicio=datetime.now(UTC) - timedelta(hours=1),
            horas_hombre=2.5,
        )

        res = await use_case.execute(empresa_id, ot_id, request)

        assert res.technician_id == tecnico_id
        assert res.tareas_realizadas == "Reemplazo de filtro de aire"
        assert res.horas_hombre == 2.5
        assert res.id is not None

        assert mock_repo.save.called
        assert mock_uow.commit.called

    async def test_create_intervention_negative_hours_fails(self, mock_uow: Any) -> None:
        use_case = CreateInterventionUseCase(uow=mock_uow)
        empresa_id = str(uuid4())
        ot_id = str(uuid4())

        with pytest.raises(ValueError, match="horas_hombre no puede ser negativo"):
            request = CreateInterventionRequest(
                technician_id=uuid4(),
                tareas_realizadas="Reemplazo",
                fecha_inicio=datetime.now(UTC) - timedelta(hours=1),
                horas_hombre=-1.0,
            )
            await use_case.execute(empresa_id, ot_id, request)


class TestGetInterventionUseCase:

    async def test_get_intervention_successful(self, mock_uow: Any, mock_repo: Any) -> None:
        company_id = CompanyId(uuid4())
        ot_id = WorkOrderId(uuid4())
        intervention_id = InterventionId(uuid4())
        tecnico_id = UserId(uuid4())

        intervention = TechnicalIntervention(
            id=intervention_id,
            empresa_id=company_id,
            work_order_id=ot_id,
            technician_id=tecnico_id,
            tareas_realizadas="Reparacion",
            fecha_inicio=datetime.now(UTC) - timedelta(hours=2),
            fecha_fin=None,
            horas_hombre=2.0,
        )
        mock_repo.get_by_id.return_value = intervention

        use_case = GetInterventionUseCase(uow=mock_uow)
        res = await use_case.execute(str(company_id.value), str(ot_id.value), str(intervention_id.value))

        assert res.id == intervention_id.value
        assert res.tareas_realizadas == "Reparacion"
        mock_repo.get_by_id.assert_called_once_with(intervention_id, company_id)

    async def test_get_intervention_not_found(self, mock_uow: Any, mock_repo: Any) -> None:
        mock_repo.get_by_id.return_value = None

        use_case = GetInterventionUseCase(uow=mock_uow)
        with pytest.raises(InterventionNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()), str(uuid4()))


class TestListInterventionsUseCase:

    async def test_list_interventions_successful(self, mock_uow: Any, mock_repo: Any) -> None:
        company_id = CompanyId(uuid4())
        ot_id = WorkOrderId(uuid4())
        tecnico_id = UserId(uuid4())

        intervention = TechnicalIntervention(
            id=InterventionId(uuid4()),
            empresa_id=company_id,
            work_order_id=ot_id,
            technician_id=tecnico_id,
            tareas_realizadas="Intervencion 1",
            fecha_inicio=datetime.now(UTC) - timedelta(hours=2),
            fecha_fin=None,
            horas_hombre=2.0,
        )
        mock_repo.get_by_work_order.return_value = [intervention]

        use_case = ListInterventionsUseCase(uow=mock_uow)
        res, total = await use_case.execute(str(company_id.value), str(ot_id.value))

        assert total == 1
        assert len(res) == 1
        assert res[0].tareas_realizadas == "Intervencion 1"
        mock_repo.get_by_work_order.assert_called_once_with(work_order_id=ot_id, empresa_id=company_id)


class TestUpdateInterventionUseCase:

    async def test_update_intervention_successful(self, mock_uow: Any, mock_repo: Any) -> None:
        company_id = CompanyId(uuid4())
        ot_id = WorkOrderId(uuid4())
        intervention_id = InterventionId(uuid4())
        tecnico_id = UserId(uuid4())

        intervention = TechnicalIntervention(
            id=intervention_id,
            empresa_id=company_id,
            work_order_id=ot_id,
            technician_id=tecnico_id,
            tareas_realizadas="Old Desc",
            fecha_inicio=datetime.now(UTC) - timedelta(hours=2),
            fecha_fin=None,
            horas_hombre=2.0,
        )
        mock_repo.get_by_id.return_value = intervention

        use_case = UpdateInterventionUseCase(uow=mock_uow)
        request = UpdateInterventionRequest(
            tareas_realizadas="New Desc",
            horas_hombre=4.0,
        )

        res = await use_case.execute(str(company_id.value), str(ot_id.value), str(intervention_id.value), request)

        assert res.tareas_realizadas == "New Desc"
        assert res.horas_hombre == 4.0

        assert mock_repo.save.called
        assert mock_uow.commit.called

    async def test_update_intervention_not_found(self, mock_uow: Any, mock_repo: Any) -> None:
        mock_repo.get_by_id.return_value = None

        use_case = UpdateInterventionUseCase(uow=mock_uow)
        request = UpdateInterventionRequest(tareas_realizadas="New Desc")

        with pytest.raises(InterventionNotFoundError):
            await use_case.execute(str(uuid4()), str(uuid4()), str(uuid4()), request)

    async def test_update_intervention_negative_hours_fails(self, mock_uow: Any, mock_repo: Any) -> None:
        company_id = CompanyId(uuid4())
        ot_id = WorkOrderId(uuid4())
        intervention_id = InterventionId(uuid4())
        tecnico_id = UserId(uuid4())

        intervention = TechnicalIntervention(
            id=intervention_id,
            empresa_id=company_id,
            work_order_id=ot_id,
            technician_id=tecnico_id,
            tareas_realizadas="Desc",
            fecha_inicio=datetime.now(UTC),
            fecha_fin=None,
            horas_hombre=2.0,
        )
        mock_repo.get_by_id.return_value = intervention

        use_case = UpdateInterventionUseCase(uow=mock_uow)

        # horas_hombre=-1.0 es truthy, replace lo pasa a __post_init__ que levanta ValueError
        request = UpdateInterventionRequest(horas_hombre=-1.0)

        with pytest.raises(ValueError, match="horas_hombre no puede ser negativo"):
            await use_case.execute(str(company_id.value), str(ot_id.value), str(intervention_id.value), request)
