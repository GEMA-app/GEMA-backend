"""Caso de uso para eliminar un reporte de falla."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions.failure_report import FailureReportNotFoundError
from app.domain.value_objects import CompanyId, FailureReportId


class DeleteFailureReportUseCase:
    """Caso de uso para eliminar un reporte de falla."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, report_id_str: str) -> None:
        """Elimina un reporte de falla por su ID.

        Args:
            company_id_str: Identificador UUID de la empresa.
            report_id_str: Identificador UUID del reporte a eliminar.

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

            await self.uow.failure_reports.delete(report_id, company_id)
            await self.uow.commit()
