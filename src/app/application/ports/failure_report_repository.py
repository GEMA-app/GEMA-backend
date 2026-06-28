"""Puerto de repositorio para FailureReport.

Define el contrato que debe implementar cualquier adapter de persistencia
de reportes de falla.
"""

from typing import Protocol

from app.domain.entities import FailureReport
from app.domain.value_objects import CompanyId, FailureReportId


class FailureReportRepositoryPort(Protocol):
    """Puerto de repositorio para la persistencia y consulta de FailureReport."""

    async def save(self, report: FailureReport) -> None:
        """Persiste un reporte de falla en la base de datos."""
        ...

    async def get_by_id(self, id: FailureReportId, empresa_id: CompanyId) -> FailureReport | None:
        """Obtiene un reporte de falla por su ID y empresa."""
        ...

    async def list_by_company(
        self, empresa_id: CompanyId, offset: int = 0, limit: int = 10,
        filters: dict[str, str] | None = None
    ) -> tuple[list[FailureReport], int]:
        """Lista reportes de falla de una empresa con paginación y filtros."""
        ...

    async def delete(self, id: FailureReportId, empresa_id: CompanyId) -> None:
        """Elimina un reporte de falla por su ID y empresa."""
        ...
