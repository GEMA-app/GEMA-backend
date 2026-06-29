"""Casos de uso para el modulo de Reportes de Falla."""
from app.application.use_cases.failure_report.create_failure_report import (
    CreateFailureReportUseCase,
)
from app.application.use_cases.failure_report.delete_failure_report import (
    DeleteFailureReportUseCase,
)
from app.application.use_cases.failure_report.get_failure_report import GetFailureReportUseCase
from app.application.use_cases.failure_report.list_failure_report import ListFailureReportsUseCase
from app.application.use_cases.failure_report.update_failure_report import (
    UpdateFailureReportUseCase,
)

__all__ = [
    "CreateFailureReportUseCase",
    "GetFailureReportUseCase",
    "ListFailureReportsUseCase",
    "UpdateFailureReportUseCase",
    "DeleteFailureReportUseCase",
]
