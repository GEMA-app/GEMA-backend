"""Tests for failure report use cases."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import UTC, datetime

import pytest

from app.application.dtos.failure_report_dtos import (
    CreateFailureReportRequest,
    UpdateFailureReportRequest,
)
from app.application.use_cases.create_failure_report import CreateFailureReportUseCase
from app.application.use_cases.delete_failure_report import DeleteFailureReportUseCase
from app.application.use_cases.get_failure_report import GetFailureReportUseCase
from app.application.use_cases.list_failure_report import ListFailureReportsUseCase
from app.application.use_cases.update_failure_report import UpdateFailureReportUseCase
from app.domain.entities.failure_report import FailureReport
from app.domain.enums import PriorityLevel, ReportStatus
from app.domain.exceptions.failure_report import (
    EmptyDescriptionError,
    EmptyLocationError,
    EmptyReportedByError,
    EmptyTitleError,
    FailureReportNotFoundError,
)
from app.domain.value_objects import CompanyId, FailureReportId


@pytest.fixture
def mock_uow() -> Any:
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.failure_reports = MagicMock()
    uow.failure_reports.save = AsyncMock()
    uow.failure_reports.get_by_id = AsyncMock()
    uow.failure_reports.list_by_company = AsyncMock()
    uow.failure_reports.delete = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCreateFailureReportUseCase:

    async def test_create_failure_report_successful(self, mock_uow: Any) -> None:
        use_case = CreateFailureReportUseCase(uow=mock_uow)
        company_id = str(uuid4())

        request = CreateFailureReportRequest(
            empresa_id=company_id,
            title="Water leak",
            description="Water leak in first floor bathroom",
            location="Ground Floor - Restrooms",
            priority="alta",
            reported_by="Juan Perez",
        )

        res = await use_case.execute(company_id, request)

        assert res.title == "Water leak"
        assert res.description == "Water leak in first floor bathroom"
        assert res.location == "Ground Floor - Restrooms"
        assert res.priority == "alta"
        assert res.reported_by == "Juan Perez"
        assert res.status == "pendiente"
        assert res.empresa_id == company_id
        assert res.id is not None

        assert mock_uow.failure_reports.save.called
        assert mock_uow.commit.called

    @pytest.mark.parametrize(
        "title,description,location,reported_by,expected_exc",
        [
            ("", "Desc", "Loc", "Rep", EmptyTitleError),
            ("Title", "", "Loc", "Rep", EmptyDescriptionError),
            ("Title", "Desc", "", "Rep", EmptyLocationError),
            ("Title", "Desc", "Loc", "", EmptyReportedByError),
        ],
    )
    async def test_create_failure_report_validations(
        self, mock_uow: Any, title: str, description: str, location: str, reported_by: str, expected_exc: Any
    ) -> None:
        use_case = CreateFailureReportUseCase(uow=mock_uow)
        company_id = str(uuid4())

        request = CreateFailureReportRequest(
            empresa_id=company_id,
            title=title,
            description=description,
            location=location,
            priority="alta",
            reported_by=reported_by,
        )

        with pytest.raises(expected_exc):
            await use_case.execute(company_id, request)


class TestGetFailureReportUseCase:

    async def test_get_failure_report_successful(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        report_id = FailureReportId(uuid4())

        report = FailureReport(
            id=report_id,
            empresa_id=company_id,
            title="Leak",
            description="Gas leak",
            location="Plant 2",
            priority=PriorityLevel.CRITICAL,
            reported_by="Jose",
            status=ReportStatus.PENDING,
            created_at=datetime.now(UTC),
        )
        mock_uow.failure_reports.get_by_id.return_value = report

        use_case = GetFailureReportUseCase(uow=mock_uow)
        res = await use_case.execute(str(company_id.value), str(report_id.value))

        assert res.id == str(report_id.value)
        assert res.title == "Leak"
        assert res.priority == "critica"
        mock_uow.failure_reports.get_by_id.assert_called_once_with(report_id, company_id)

    async def test_get_failure_report_not_found(self, mock_uow: Any) -> None:
        company_id = str(uuid4())
        report_id = str(uuid4())
        mock_uow.failure_reports.get_by_id.return_value = None

        use_case = GetFailureReportUseCase(uow=mock_uow)
        with pytest.raises(FailureReportNotFoundError):
            await use_case.execute(company_id, report_id)


class TestListFailureReportsUseCase:

    async def test_list_failure_reports_successful(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        report1 = FailureReport(
            id=FailureReportId(uuid4()),
            empresa_id=company_id,
            title="Report 1",
            description="Desc 1",
            location="Loc 1",
            priority=PriorityLevel.LOW,
            reported_by="Jose",
            status=ReportStatus.PENDING,
            created_at=datetime.now(UTC),
        )
        mock_uow.failure_reports.list_by_company.return_value = ([report1], 1)

        use_case = ListFailureReportsUseCase(uow=mock_uow)
        reports, total = await use_case.execute(str(company_id.value), 0, 10, {"status": "pendiente"})

        assert total == 1
        assert len(reports) == 1
        assert reports[0].title == "Report 1"
        mock_uow.failure_reports.list_by_company.assert_called_once_with(
            company_id, 0, 10, {"status": "pendiente"}
        )


class TestUpdateFailureReportUseCase:

    async def test_update_failure_report_successful(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        report_id = FailureReportId(uuid4())

        report = FailureReport(
            id=report_id,
            empresa_id=company_id,
            title="Old Title",
            description="Old Desc",
            location="Old Loc",
            priority=PriorityLevel.LOW,
            reported_by="Old Rep",
            status=ReportStatus.PENDING,
            created_at=datetime.now(UTC),
        )
        mock_uow.failure_reports.get_by_id.return_value = report

        use_case = UpdateFailureReportUseCase(uow=mock_uow)
        request = UpdateFailureReportRequest(
            title="New Title",
            status="en_proceso",
            priority="alta",
        )

        res = await use_case.execute(str(company_id.value), str(report_id.value), request)

        assert res.title == "New Title"
        assert res.status == "en_proceso"
        assert res.priority == "alta"
        assert res.description == "Old Desc"  # unmodified

        assert mock_uow.failure_reports.save.called
        assert mock_uow.commit.called

    async def test_update_failure_report_not_found(self, mock_uow: Any) -> None:
        company_id = str(uuid4())
        report_id = str(uuid4())
        mock_uow.failure_reports.get_by_id.return_value = None

        use_case = UpdateFailureReportUseCase(uow=mock_uow)
        request = UpdateFailureReportRequest(title="New Title")

        with pytest.raises(FailureReportNotFoundError):
            await use_case.execute(company_id, report_id, request)


class TestDeleteFailureReportUseCase:

    async def test_delete_failure_report_successful(self, mock_uow: Any) -> None:
        company_id = CompanyId(uuid4())
        report_id = FailureReportId(uuid4())

        report = FailureReport(
            id=report_id,
            empresa_id=company_id,
            title="Title",
            description="Desc",
            location="Loc",
            priority=PriorityLevel.LOW,
            reported_by="Rep",
            status=ReportStatus.PENDING,
            created_at=datetime.now(UTC),
        )
        mock_uow.failure_reports.get_by_id.return_value = report

        use_case = DeleteFailureReportUseCase(uow=mock_uow)
        await use_case.execute(str(company_id.value), str(report_id.value))

        mock_uow.failure_reports.delete.assert_called_once_with(report_id, company_id)
        assert mock_uow.commit.called

    async def test_delete_failure_report_not_found(self, mock_uow: Any) -> None:
        company_id = str(uuid4())
        report_id = str(uuid4())
        mock_uow.failure_reports.get_by_id.return_value = None

        use_case = DeleteFailureReportUseCase(uow=mock_uow)

        with pytest.raises(FailureReportNotFoundError):
            await use_case.execute(company_id, report_id)
