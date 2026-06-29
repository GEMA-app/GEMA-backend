"""Caso de uso para crear un reporte de falla."""

from app.application.dtos.failure_report_dtos import (
    CreateFailureReportRequest,
    FailureReportResponse,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import FailureReport
from app.domain.enums import PriorityLevel
from app.domain.value_objects import AssetId, CompanyId


class CreateFailureReportUseCase:
    """Caso de uso para crear un nuevo reporte de falla en una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Inicializa el caso de uso con una unidad de trabajo."""
        self.uow = uow

    async def execute(
        self, company_id_str: str, request: CreateFailureReportRequest
    ) -> FailureReportResponse:
        """Crea un reporte de falla y lo persiste en la base de datos.

        Args:
            company_id_str: Identificador UUID de la empresa en formato string.
            request: DTO con los datos del reporte de falla a crear.

        Returns:
            DTO de respuesta con los datos completos del reporte creado.

        Raises:
            EmptyTitleError: Si el titulo esta vacio.
            EmptyDescriptionError: Si la descripcion esta vacia.
            EmptyLocationError: Si la ubicacion esta vacia.
            EmptyReportedByError: Si el reportante esta vacio.
        """
        company_id = CompanyId.from_string(company_id_str)
        priority = PriorityLevel(request.priority.lower())
        activo_id = AssetId.from_string(request.activo_id) if request.activo_id else None

        async with self.uow:
            report = FailureReport.create(
                empresa_id=company_id,
                title=request.title.strip(),
                description=request.description.strip(),
                location=request.location.strip(),
                priority=priority,
                reported_by=request.reported_by.strip(),
                activo_id=activo_id,
            )

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
                activo_id=str(report.activo_id) if report.activo_id else None,
                version=report.version,
            )
