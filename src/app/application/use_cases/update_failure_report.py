"""Caso de uso para actualizar un reporte de falla."""

from app.application.dtos.failure_report_dtos import (
    FailureReportResponse,
    UpdateFailureReportRequest,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.enums import PriorityLevel, ReportStatus
from app.domain.exceptions.failure_report import FailureReportNotFoundError
from app.domain.value_objects import CompanyId, FailureReportId


class UpdateFailureReportUseCase:
    """Caso de uso para actualizar un reporte de falla."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id_str: str,
        report_id_str: str,
        request: UpdateFailureReportRequest,
    ) -> FailureReportResponse:
        """Actualiza parcialmente un reporte de falla existente.

        Args:
            company_id_str: Identificador UUID de la empresa.
            report_id_str: Identificador UUID del reporte a actualizar.
            request: DTO con los campos a modificar y su conjunto de campos definidos.

        Returns:
            DTO con los datos completos del reporte actualizado.

        Raises:
            FailureReportNotFoundError: Si el reporte no existe en la empresa.
        """
        company_id = CompanyId.from_string(company_id_str)
        report_id = FailureReportId.from_string(report_id_str)

        async with self.uow:
            report = await self.uow.failure_reports.get_by_id(report_id, company_id)
            if not report:
                raise FailureReportNotFoundError(
                    f"El reporte de falla con ID '{report_id_str}' no existe en esta empresa."
                )

            if "title" in request._fields_set and request.title is not None:
                report.title = request.title.strip()
            if "description" in request._fields_set and request.description is not None:
                report.description = request.description.strip()
            if "location" in request._fields_set and request.location is not None:
                report.location = request.location.strip()
            if "priority" in request._fields_set and request.priority is not None:
                report.priority = PriorityLevel(request.priority.lower())
            if "reported_by" in request._fields_set and request.reported_by is not None:
                report.reported_by = request.reported_by.strip()
            if "status" in request._fields_set and request.status is not None:
                report.status = ReportStatus(request.status.lower())

            await self.uow.failure_reports.save(report)
            await self.uow.commit()

            return FailureReportResponse(
                id=str(report.id),
                empresa_id=str(report.empresa_id),
                title=report.title,
                description=report.description,
                location=report.location,
                priority=report.priority.value,
                reported_by=report.reported_by,
                status=report.status.value,
                created_at=report.created_at.isoformat() if report.created_at else "",
            )
