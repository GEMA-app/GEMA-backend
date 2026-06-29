"""Fábricas de dependencias para casos de uso de reportes de falla."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.failure_report import (
    CreateFailureReportUseCase,
    DeleteFailureReportUseCase,
    GetFailureReportUseCase,
    ListFailureReportsUseCase,
    UpdateFailureReportUseCase,
)
from app.composition.container.common import get_uow


async def get_create_failure_report_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateFailureReportUseCase:
    """Fábrica que inyecta la unidad de trabajo en CreateFailureReportUseCase."""
    return CreateFailureReportUseCase(uow)


async def get_failure_report_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetFailureReportUseCase:
    """Fábrica que inyecta la unidad de trabajo en GetFailureReportUseCase."""
    return GetFailureReportUseCase(uow)


async def get_list_failure_reports_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListFailureReportsUseCase:
    """Fábrica que inyecta la unidad de trabajo en ListFailureReportsUseCase."""
    return ListFailureReportsUseCase(uow)


async def get_update_failure_report_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateFailureReportUseCase:
    """Fábrica que inyecta la unidad de trabajo en UpdateFailureReportUseCase."""
    return UpdateFailureReportUseCase(uow)


async def get_delete_failure_report_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteFailureReportUseCase:
    """Fábrica que inyecta la unidad de trabajo en DeleteFailureReportUseCase."""
    return DeleteFailureReportUseCase(uow)

