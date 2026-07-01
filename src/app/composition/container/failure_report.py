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
    """Fábrica de dependencias para el caso de uso de creación de reporte de falla.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreateFailureReportUseCase.
    """
    return CreateFailureReportUseCase(uow)


async def get_failure_report_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetFailureReportUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de reporte de falla.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetFailureReportUseCase.
    """
    return GetFailureReportUseCase(uow)


async def get_list_failure_reports_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListFailureReportsUseCase:
    """Fábrica de dependencias para el caso de uso de listado de reportes de falla.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListFailureReportsUseCase.
    """
    return ListFailureReportsUseCase(uow)


async def get_update_failure_report_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateFailureReportUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de reporte de falla.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateFailureReportUseCase.
    """
    return UpdateFailureReportUseCase(uow)


async def get_delete_failure_report_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteFailureReportUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de reporte de falla.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteFailureReportUseCase.
    """
    return DeleteFailureReportUseCase(uow)
