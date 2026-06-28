"""Caso de uso para listar reportes de falla con paginación y filtros."""


from app.application.dtos.failure_report_dtos import FailureReportResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListFailureReportsUseCase:
    """Caso de uso para listar reportes de falla con paginación y filtros."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self,
        company_id_str: str,
        offset: int,
        limit: int,
        filters: dict[str, str] | None = None,
    ) -> tuple[list[FailureReportResponse], int]:
        """Lista reportes de falla con paginación y filtros opcionales.

        Args:
            company_id_str: Identificador UUID de la empresa.
            offset: Número de registros a omitir.
            limit: Máximo de registros a retornar.
            filters: Diccionario opcional con filtros (status, priority, search).

        Returns:
            Tupla con la lista de DTOs de respuesta y el conteo total de registros.
        """
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            reports, total = await self.uow.failure_reports.list_by_company(
                company_id, offset, limit, filters
            )

            responses = [
                FailureReportResponse(
                    id=str(r.id),
                    empresa_id=str(r.empresa_id),
                    title=r.title,
                    description=r.description,
                    location=r.location,
                    priority=r.priority.value,
                    reported_by=r.reported_by,
                    status=r.status.value,
                    created_at=r.created_at.isoformat() if r.created_at else "",
                )
                for r in reports
            ]
            return responses, total
