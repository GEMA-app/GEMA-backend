"""Caso de uso para obtener un reporte de falla por ID."""

from app.application.dtos.failure_report_dtos import FailureReportResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.failure_report import FailureReportNotFoundError
from app.domain.value_objects import CompanyId, FailureReportId


class GetFailureReportUseCase:
    """Caso de uso para obtener un reporte de falla por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, report_id_str: str
    ) -> FailureReportResponse:
        """Obtiene un reporte de falla por su ID.

        Args:
            company_id_str: Identificador UUID de la empresa.
            report_id_str: Identificador UUID del reporte de falla.

        Returns:
            DTO con los datos completos del reporte encontrado.

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
